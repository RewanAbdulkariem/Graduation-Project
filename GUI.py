"""
GUI.py
"""
import sys
import os
import cv2, imutils
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel,QTabWidget
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QThread,pyqtSignal as Signal,pyqtSlot as Slot
from Barcode_Product_Recognition.Video_predict import Barcodeframe 
from Fire_Detection.fire_detection import fireframe
from ultralytics import YOLO

video_path = None               # Global variable to be used in both classes 
selected_model = "Barcode Recognition"
safety_models = ['Vest and Helmet Detection', 'Crowd Detection', 'Fire Detection']
production_models = ['Defects Classification', 'Defect Detection', 'Barcode Recognition']

class MainWindow(QMainWindow):
    """Main window class for the Object Detection and Barcode Reader application."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        uic.loadUi("App.ui", self)
        self.initUI()

    def initUI(self):
        """Initialize the user interface components."""
        self.Pc_VideoButton.clicked.connect(self.openFile)
        self.Pc_LiveButton.clicked.connect(self.openCamera)

        self.Pc_modelBox.currentIndexChanged.connect(self.decide_model)

        self.Sf_VideoButton.clicked.connect(self.openFile)
        self.Sf_LiveButton.clicked.connect(self.openCamera)

        self.Sf_modelBox.currentIndexChanged.connect(self.decide_model)

        # Create an instance of VideoThread to handle video processing
        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.displayFrame)

    def decide_model(self):
        global selected_model

        selected_model =  self.Pc_modelBox.currentText()
        self.start_video_processing()

    def openFile(self):
            print("clicked")
            """Open a video file using a file dialog."""
            global video_path
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)", options=options)
            if fileName:
                video_path = fileName
                self.start_video_processing()

    def openCamera(self):
        """Open the default camera for video capture."""
        global video_path

        video_path = None
        self.start_video_processing()

    def start_video_processing(self):
        """Start video processing using a separate thread."""
        global video_path

        if self.video_thread.isRunning():
            self.video_thread.terminate()
            self.video_thread.wait()

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.displayFrame)
        self.video_thread.start()

    @Slot(QImage)
    def displayFrame(self, image):
        """Display the processed video frame on the QLabel."""
        global selected_model, safety_models, production_models

        pixmap = QPixmap.fromImage(image)
        if selected_model in safety_models:
            self.Sf_label.setPixmap(pixmap)
        elif selected_model in production_models:
            self.Pc_label.setPixmap(pixmap)

class VideoThread(QThread):
    """Thread for video processing."""
    frame_signal = Signal(QImage)

    def run(self):
        """Run the video processing thread."""
        self.model_exc()
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            processed_frame = self.prediction(frame)

            if processed_frame is not None:
                processed_frame = self.cvimage_to_label(processed_frame)
                self.frame_signal.emit(processed_frame)
    def prediction(self, frame):
        """predict accroding to model"""
        if selected_model == 'Defects Classification':
                #return os.path.join('.', 'path_to_defects_classification_model')
            pass
        elif selected_model == 'Defect Detection':
            #return os.path.join()
            pass
        elif selected_model == 'Barcode Recognition':
            return Barcodeframe(frame, self.model)
        elif selected_model == 'Vest and Helmet Detection':
            pass
        elif selected_model == 'Crowd Detection':
            pass
        elif selected_model == 'Fire Detection':
            return fireframe(frame, self.model)

    def cvimage_to_label(self,image):
        """Convert an OpenCV image to a QImage suitable for displaying."""
        if image is None:
            return QImage()
        image = imutils.resize(image,width = 640)
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image = QImage(image,
                       image.shape[1],
                       image.shape[0],
                       QImage.Format_RGB888)
        return image
    
    def model_exc(self):
        """Load the YOLO object detection model."""
        global video_path

        model_path =self.get_model_path()
        self.model = self.load_model(model_path)

        if video_path is None:
            self.cap = cv2.VideoCapture(0)  # Use default camera
        else:
            self.cap = cv2.VideoCapture(video_path)

    def get_model_path(self):
            global selected_model
            print("change model: ", selected_model)

            """Get the model path based on the selected model."""
            if selected_model == 'Defects Classification':
                #return os.path.join('.', 'path_to_defects_classification_model')
                pass
            elif selected_model == 'Defect Detection':
                #return os.path.join()
                pass
            elif selected_model == 'Barcode Recognition':
                return os.path.join('.','Barcode_Product_Recognition', 'runs', 'detect', 'train', 'weights', 'last.pt')
            elif selected_model == 'Vest and Helmet Detection':
                pass
            elif selected_model == 'Crowd Detection':
                pass
            elif selected_model == 'Fire Detection':
                return os.path.join('.', 'Fire_Detection', 'fire.pt')

    def load_model(self, model_path):
            """Load the appropriate model."""
            if model_path:
                return YOLO(model_path)
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
