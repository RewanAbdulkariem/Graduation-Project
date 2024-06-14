import os
import cv2
import cvzone
import math
import argparse
from ultralytics import YOLO

def parse_arguments():
    """Parse command-line arguments."""
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the (optional) video file")
    args = vars(ap.parse_args())
    return args

def initialize_video_capture(video_path=None):
    """Initialize video capture object based on specified video path or camera."""
    if video_path is None:
        cap = cv2.VideoCapture(0)  # Use default camera
    else:
        cap = cv2.VideoCapture(video_path)
    return cap

def load_safety_model(model_path):
    """Load fire detection model."""
    model = YOLO(model_path)
    return model

def Safetyframe(frame, model, threshold=50):
    """Detect fire in a single frame and annotate with bounding boxes."""
    results = model(frame, stream=True, verbose=False)
    classnames = ['fall', 'Safty-Vest', 'Helmet', 'without_Helmet', 'without_Safty-Vest']

    for info in results:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if confidence > threshold:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100],
                                   scale=1.5, thickness=2)

    return frame

def SafetyPredictor():
    """Process video frames for fire detection."""
    args = parse_arguments()
    video_path = args.get("video", None)

    model_path = r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt'
    
    model = load_safety_model(model_path)
    cap = initialize_video_capture(video_path)

    if not cap.isOpened():
        print("Error opening video capture.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = Safetyframe(frame, model)
        cv2.imshow("Fire Detection", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    SafetyPredictor()