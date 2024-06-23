"""
GUI.py
"""
from time import time
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog,  QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot as Slot, Qt

from Serial import SerialThread
from email_safety import send_email_async
from VideoProcessing import VideoThread

class MainWindow(QMainWindow):
    """Main window class for the Object Detection and Barcode Reader application."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        uic.loadUi("App.ui", self)
        self.initUI()

    def initUI(self):
        """Initialize the user interface components."""
        self.intialize_values()
        self.handle_signals()

        # Create an instance of VideoThread to handle video processing
        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.displayFrame)

        self.serial_thread = SerialThread()
        self.serial_thread.data_received.connect(self.update_gui)
        self.serial_thread.start()

    def intialize_values(self):
        self.video_path = None
        self.selected_model = 'Safety of workers'
        self.tabIndex = 1
        self.threshold = 50
        self.last_email_time = 0
        self.email_interval = 60

        self.tempLCD.display(0)
        self.humLCD.display(0)

        self.tabWidget.setCurrentIndex(self.tabIndex)

        self.Sf_confBox.setValue(self.threshold)
        self.Pc_confBox.setValue(self.threshold)

        self.Sf_confSlider.setValue(self.threshold)
        self.Pc_confSlider.setValue(self.threshold)

    def handle_signals(self):
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.Pc_VideoButton.clicked.connect(self.openFile)
        self.Pc_LiveButton.clicked.connect(self.openCamera)
        self.Pc_modelBox.currentIndexChanged.connect(self.decide_model)
        self.Pc_confBox.valueChanged.connect(self.changethreshold)
        self.Pc_confSlider.valueChanged.connect(self.changethreshold)
        self.Pc_StopButton.clicked.connect(self.stopVideoProcessing)
        self.Pc_StartButton.clicked.connect(self.resumeVideoProcessing)

        self.Sf_VideoButton.clicked.connect(self.openFile)
        self.Sf_LiveButton.clicked.connect(self.openCamera)
        self.Sf_modelBox.currentIndexChanged.connect(self.decide_model)
        self.Sf_confBox.valueChanged.connect(self.changethreshold)
        self.Sf_confSlider.valueChanged.connect(self.changethreshold)
        self.Sf_StopButton.clicked.connect(self.stopVideoProcessing)
        self.Sf_StartButton.clicked.connect(self.resumeVideoProcessing)

    @Slot(float, float, float, float, float, float,)
    def update_gui(self, temperature, humidity, LPG, CH4, CO, Smoke):
        self.tempLCD.display(temperature)
        self.humLCD.display(humidity)
        self.LPGLCD.display(LPG)
        self.CH4LCD.display(CH4)
        self.COLCD.display(CO)
        self.SmokeLCD.display(Smoke)
        current_time = time()
        if current_time - self.last_email_time >= self.email_interval:
            self.last_email_time = current_time
            # Check if temperature exceeds 38 degrees
            if temperature > 38:
                self.show_warning("High Temperature Warning", f"Temperature has exceeded safe levels: {temperature} °C")
                send_email_async(f"Temperature has exceeded safe levels: {temperature} °C", None)

            # Check if CO exceeds 120 ppm
            if CO > 120:
                self.show_warning("High CO Warning", f"CO levels have exceeded safe levels: {CO} ppm")
                send_email_async(f"CO levels have exceeded safe levels: {CO} ppm", None)

            # Check if CH4 exceeds 1000 ppm
            if CH4 > 1000:
                self.show_warning("High CH4 Warning", f"CH4 levels have exceeded safe levels: {CH4} ppm")
                send_email_async(f"CH4 levels have exceeded safe levels: {CH4} ppm", None)

            # Check if Smoke exceeds 500 ppm
            if Smoke > 500:
                self.show_warning("High Smoke Warning", f"Smoke levels have exceeded safe levels: {Smoke} ppm")
                send_email_async( f"Smoke levels have exceeded safe levels: {Smoke} ppm", None)

    def show_warning(self, title, message):
        """Show a warning message box."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def stopVideoProcessing(self):
        """Stop the video processing."""
        self.video_thread.pause()
    
    def resumeVideoProcessing(self):
        """Resume the video processing."""
        self.video_thread.resume()

    def changethreshold(self):
        """Change the confidence threshold for the selected model."""
        if self.tabIndex == 0:
            #self.serial_thread.start()
            return
        elif self.tabIndex == 1:
            if self.threshold != self.Sf_confBox.value():
                self.threshold = self.Sf_confBox.value()
                self.Sf_confSlider.setValue(self.threshold)
            else:
                self.threshold = self.Sf_confSlider.value()
                self.Sf_confBox.setValue(self.threshold)

        elif self.tabIndex == 2:
            if self.threshold != self.Pc_confBox.value():
                self.threshold = self.Pc_confBox.value()
                self.Pc_confSlider.setValue(self.threshold)
            else:
                self.threshold = self.Pc_confSlider.value()
                self.Pc_confBox.setValue(self.threshold)
        self.video_thread.update_parameters(self.video_path, self.selected_model, self.threshold)

    def on_tab_changed(self, index):
        """Handle tab change event."""
        self.tabIndex = index
        self.decide_model()

    def decide_model(self):
        """Decide which model to use based on the current tab and dropdown selection."""
        if self.tabIndex == 0:
            return
        if self.tabIndex == 1:
            self.selected_model = self.Sf_modelBox.currentText()
        elif self.tabIndex == 2:
            self.selected_model = self.Pc_modelBox.currentText()
        self.start_video_processing()

    def openFile(self):
        """Open a video file using a file dialog."""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.jpg *.png *.jpeg)", options=options)
        if fileName:
            self.video_path = fileName
            self.start_video_processing()
        else:
            print("Error: No file selected.")

    def openCamera(self):
        """Open the default camera for video capture."""
        self.video_path = None
        self.start_video_processing()

    def start_video_processing(self):
        """Start video processing using a separate thread."""
        if self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.displayFrame)
        self.video_thread.update_parameters(self.video_path, self.selected_model, self.threshold)
        self.video_thread.start()

    @Slot(QImage)
    def displayFrame(self, image):
        """Display the processed video frame on the QLabel."""
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(1280, 720, transformMode=Qt.SmoothTransformation)
        if self.tabIndex == 1:
            self.Sf_label.setPixmap(scaled_pixmap)
        if self.tabIndex == 2:
            self.Pc_label.setPixmap(scaled_pixmap)
