"""
GUI.py
"""
import sys
import cv2

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal as Signal, pyqtSlot as Slot

from Barcode_Product_Recognition.Barcode_predict import Barcodeframe
from Fire_Detection.fire_detection import fireframe
from Safety_of_workers.Safety import Safety_frame
from Crowd_Detection.crowd_detection import load_class_list, detect_and_track
from Crowd_Detection.tracker import Tracker

from Defects_Detection.defect_detection import defectframe
from Defects_Classification.defect_class import defectclassframe
from ultralytics import YOLO
from Serial import SerialThread

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

    @Slot(int, int)
    def update_gui(self, temperature, humidity):
        self.tempLCD.display(temperature)
        self.humLCD.display(humidity)

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
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)", options=options)
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
        if self.tabIndex == 1:
            self.Sf_label.setPixmap(pixmap)
        if self.tabIndex == 2:
            self.Pc_label.setPixmap(pixmap)

class VideoThread(QThread):
    """Thread for video processing."""
    frame_signal = Signal(QImage)

    def __init__(self):
        """Initialize the video thread."""
        super().__init__()
        self.cap = None
        self.model = None
        self.running = True
        self.paused = False
        self.class_list = load_class_list(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Crowd_Detection\coco.txt')
        self.tracker = Tracker()
        self.model_map = {
            'Safety of workers': [YOLO( r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt'),
                                        YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Awakeness_Detection\best.pt')],
            'Crowd Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Crowd_Detection\yolov8s.pt'),
            'Defect Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Detection\defectdetection.pt'),
            'Defects Classifictaion': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Classification\defectClassification.pt'),
            'Barcode Recognition': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Barcode_Product_Recognition\last.pt'),
            'Fire Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Fire_Detection\fire.pt')
    }

    def update_parameters(self, video_path, selected_model, threshold):
        """Update the thread parameters."""
        self.video_path = video_path
        self.selected_model = selected_model
        self.threshold = threshold

    def run(self):
        """Run the video processing thread."""
        self.load_model()
        if self.cap is None:
            return

        while self.running:
            if self.paused:
                self.msleep(100)
                continue

            ret, frame = self.cap.read()
            if not ret:
                break

            processed_frame = self.prediction(frame)
            if processed_frame is not None:
                processed_frame = self.cvimage_to_label(processed_frame)
                self.frame_signal.emit(processed_frame)
            QThread.msleep(1)

        self.cap.release()

    def stop(self):
        """Stop the thread."""
        self.running = False

    def resume(self):
        """Resume the video processing."""
        self.paused = False

    def pause(self):
        """Pause the video processing."""
        self.paused = True

    def prediction(self, frame):
        """Perform prediction according to the selected model."""
        if self.selected_model == 'Defects Classifictaion':
            return defectclassframe(frame, self.model, self.threshold)
        elif self.selected_model == 'Defect Detection':
            return defectframe(frame, self.model)
        elif self.selected_model == 'Barcode Recognition':
            return Barcodeframe(frame, self.model, self.threshold)
        elif self.selected_model == 'Safety of workers':
            frame = Safety_frame(frame, self.model[0], ['fall', 'Safty-Vest', 'Helmet', 'without_Helmet', 'without_Safty-Vest'], self.threshold)
            frame = Safety_frame(frame, self.model[1], ['Drowsy', 'Awake', 'Fainted'], self.threshold)
            return frame
        elif self.selected_model == 'Crowd Detection':
            return detect_and_track(frame, self.model, self.class_list, self.tracker)
        elif self.selected_model == 'Fire Detection':
            return fireframe(frame, self.model, self.threshold)

    def cvimage_to_label(self, image):
        """Convert an OpenCV image to a QImage suitable for displaying."""
        if image is None:
            return QImage()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image

    def load_model(self):
        """Load the appropriate model based on the selected model."""
        model = self.model_map.get(self.selected_model)
        if not model:
            print(f"Error: Model for '{self.selected_model}' not found.")
            return

        self.model = model
        if self.video_path is None:
            self.cap = cv2.VideoCapture(0)  # Use default camera
        else:
            self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            print(f"Error: Failed to open video source '{self.video_path}'.")
            self.running = False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def main():
    """Main function to initialize the application."""
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()