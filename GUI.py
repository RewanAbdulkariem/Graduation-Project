"""
GUI.py
"""
import sys
import os
import cv2
import imutils

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal as Signal, pyqtSlot as Slot

from Barcode_Product_Recognition.Barcode_predict import Barcodeframe
from Fire_Detection.fire_detection import fireframe
from Safety_of_workers.Safety import Safety_frame
from Crowd_Detection.crowd_detection import load_crowd_model, load_class_list, detect_and_track
from Crowd_Detection.tracker import Tracker

from ultralytics import YOLO

class MainWindow(QMainWindow):
    """Main window class for the Object Detection and Barcode Reader application."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        uic.loadUi("App.ui", self)
        self.initUI()

    def initUI(self):
        """Initialize the user interface components."""
        self.tabIndex = 1
        self.video_path = None
        self.selected_model = 'Safety of workers'

        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.Pc_VideoButton.clicked.connect(self.openFile)
        self.Pc_LiveButton.clicked.connect(self.openCamera)
        self.Pc_modelBox.currentIndexChanged.connect(self.decide_model)
        self.Sf_VideoButton.clicked.connect(self.openFile)
        self.Sf_LiveButton.clicked.connect(self.openCamera)
        self.Sf_modelBox.currentIndexChanged.connect(self.decide_model)

        # Create an instance of VideoThread to handle video processing
        self.video_thread = VideoThread(self.video_path, self.selected_model)
        self.video_thread.frame_signal.connect(self.displayFrame)

    def on_tab_changed(self, index):
        """Handle tab change event."""
        self.tabIndex = index
        self.decide_model()

    def decide_model(self):
        """Decide which model to use based on the current tab and dropdown selection."""
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

    def openCamera(self):
        """Open the default camera for video capture."""
        self.video_path = None
        self.start_video_processing()

    def start_video_processing(self):
        """Start video processing using a separate thread."""
        if self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()

        self.video_thread = VideoThread(self.video_path, self.selected_model)
        self.video_thread.frame_signal.connect(self.displayFrame)
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

    def __init__(self, video_path, selected_model):
        super().__init__()
        self.video_path = video_path
        self.selected_model = selected_model
        self.helmet_vest_model = YOLO( r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt')
        self.drowsy_model = YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Awakeness_Detection\best.pt')
        self.crowd_model = load_crowd_model(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Crowd_Detection\yolov8s.pt')
        self.class_list = load_class_list(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Crowd_Detection\coco.txt')
        self.tracker = Tracker()
        self.cap = None
        self.model = None
        self.running = True

    def run(self):
        """Run the video processing thread."""
        self.load_model()
        if self.cap is None:
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            processed_frame = self.prediction(frame)
            if processed_frame is not None:
                processed_frame = self.cvimage_to_label(processed_frame)
                self.frame_signal.emit(processed_frame)

        self.cap.release()

    def stop(self):
        """Stop the thread."""
        self.running = False

    def prediction(self, frame):
        """Perform prediction according to the selected model."""
        if self.selected_model == 'Defects Classification':
            # Add implementation for Defects Classification
            pass
        elif self.selected_model == 'Defect Detection':
            # Add implementation for Defect Detection
            pass
        elif self.selected_model == 'Barcode Recognition':
            return Barcodeframe(frame, self.model)
        elif self.selected_model == 'Safety of workers':
            frame = Safety_frame(frame, self.helmet_vest_model, ['fall', 'Safty-Vest', 'Helmet', 'without_Helmet', 'without_Safty-Vest'])
            frame = Safety_frame(frame, self.drowsy_model, ['drowsy', 'awake', 'fainted'])
            return frame
        elif self.selected_model == 'Crowd Detection':
            return detect_and_track(frame, self.crowd_model, self.class_list, self.tracker)
        elif self.selected_model == 'Fire Detection':
            return fireframe(frame, self.model)

    def cvimage_to_label(self, image):
        """Convert an OpenCV image to a QImage suitable for displaying."""
        if image is None:
            return QImage()
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image

    def load_model(self):
        """Load the appropriate model based on the selected model."""
        model_path = self.get_model_path()
        if model_path:
            self.model = YOLO(model_path)
        if self.video_path is None:
            self.cap = cv2.VideoCapture(0)  # Use default camera
        else:
            self.cap = cv2.VideoCapture(self.video_path)

    def get_model_path(self):
        """Get the model path based on the selected model."""
        if self.selected_model == 'Defects Classification':
            # Return path to Defects Classification model
            pass
        elif self.selected_model == 'Defect Detection':
            # Return path to Defect Detection model
            pass
        elif self.selected_model == 'Barcode Recognition':
            return os.path.join('.', 'Barcode_Product_Recognition', 'runs', 'detect', 'train', 'weights', 'last.pt')
        elif self.selected_model == 'Fire Detection':
            return os.path.join('.', 'Fire_Detection', 'fire.pt')
        else:
            return None

def main():
    """Main function to initialize the application."""
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
