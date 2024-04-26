"""
GUI.py
"""
import sys
import os
import cv2, imutils
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QThread,pyqtSignal as Signal,pyqtSlot as Slot
from Video_predict import process_frame, load_yolo_model

video_path = None               # Global variable to be used in both classes 
class MainWindow(QMainWindow):
    """Main window class for the Object Detection and Barcode Reader application."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("Object Detection and Barcode Reader")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        """Initialize the user interface components."""

        # Create buttons for opening a video file and starting camera
        self.openFileButton = QPushButton('Open Video File', self)
        self.openFileButton.setGeometry(300, 550, 200, 50)
        self.openFileButton.clicked.connect(self.openFile)

        self.openCameraButton = QPushButton('Open Camera', self)
        self.openCameraButton.setGeometry(100, 550, 200, 50)
        self.openCameraButton.clicked.connect(self.openCamera)

        # Create a label widget to display video frames
        self.label = QLabel(self)
        self.label.setGeometry(50, 50, 700, 500)

        # Create an instance of VideoThread to handle video processing
        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.displayFrame)

    def openFile(self):
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
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)

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

            processed_frame = process_frame(frame, self.model)

            if processed_frame is not None:
                processed_frame = self.cvimage_to_label(processed_frame)
                self.frame_signal.emit(processed_frame)
    
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
        model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')
        self.model = load_yolo_model(model_path)

        if video_path is None:
            self.cap = cv2.VideoCapture(0)  # Use default camera
        else:
            self.cap = cv2.VideoCapture(video_path)


def main():
    """Main function to initialize the application."""
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
