from FrameProcessing import PredictionThread
from PyQt5.QtCore import QThread, pyqtSignal as Signal, pyqtSlot as Slot, QThread
from PyQt5.QtGui import QImage
from ultralytics import YOLO
import cv2


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
        self.model_map = {
            'Safety of workers': [YOLO( r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt'),
                                        YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Awakeness_Detection\best.pt')],
            'Crowd Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Crowd_Detection\yolov8s.pt'),
            'Defect Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Detection\defectdetection.pt'),
            'Defects Classifictaion': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Classification\defectClassification.pt'),
            'Barcode Recognition': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Barcode_Product_Recognition\last.pt'),
            'Fire Detection': YOLO(r'C:\Users\rewan\Downloads\GP\Graduation-Project\Fire_Detection\fire.pt')
    }
        self.prediction_thread = None
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

            if self.prediction_thread is None or not self.prediction_thread.isRunning():
                self.prediction_thread = PredictionThread(self.model, self.selected_model, frame, self.threshold)
                self.prediction_thread.prediction_complete.connect(self.process_prediction)
                self.prediction_thread.start()
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

    @Slot(object)
    def process_prediction(self, result):
        processed_frame = self.cvimage_to_label(result)
        self.frame_signal.emit(processed_frame)

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
