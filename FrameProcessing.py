from PyQt5.QtCore import QThread, pyqtSignal
from Barcode_Product_Recognition.Barcode_predict import Barcodeframe
from Fire_Detection.fire_detection import fireframe
from Safety_of_workers.Safety import Safety_frame
from Crowd_Detection.crowd_detection import load_class_list, detect_and_track
from Crowd_Detection.tracker import Tracker

from Defects_Detection.defect_detection import defectframe
from Defects_Classification.defect_class import defectclassframe
import os

class PredictionThread(QThread):
    prediction_complete = pyqtSignal(object)

    def __init__(self, model, selected_model, frame, threshold=0):
        super().__init__()
        self.model = model
        self.selected_model = selected_model
        self.frame = frame
        self.threshold = threshold
        self.initialize_resources()

    def initialize_resources(self):
        """Initialize resources like class lists and trackers based on the selected model."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        if self.selected_model == 'Crowd Detection':
            try:
                self.class_list = load_class_list(os.path.join(base_path, 'Crowd_Detection', 'coco.txt'))
                self.tracker = Tracker()
            except Exception as e:
                print(f"Error initializing resources for Crowd Detection: {e}")

    def run(self):
        # Perform the prediction based on the selected model
        if self.selected_model == 'Defects Classifictaion':
            result = defectclassframe(self.frame, self.model, self.threshold)
        elif self.selected_model == 'Defect Detection':
            result = defectframe(self.frame, self.model)
        elif self.selected_model == 'Barcode Recognition':
            result = Barcodeframe(self.frame, self.model, self.threshold)
        elif self.selected_model == 'Safety of workers':
            frame = Safety_frame(self.frame, self.model[0], ['fall', 'Safty-Vest', 'Helmet', 'without_Helmet', 'without_Safty-Vest'], self.threshold)
            frame = Safety_frame(frame, self.model[1], ['Drowsy', 'Awake', 'Fainted'], self.threshold)
            result = frame
        elif self.selected_model == 'Crowd Detection':
            result = detect_and_track(self.frame, self.model, self.class_list, self.tracker)
        elif self.selected_model == 'Fire Detection':
            result = fireframe(self.frame, self.model, self.threshold)

        self.prediction_complete.emit(result)