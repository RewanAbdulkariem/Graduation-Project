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

def load_model(model_path):
    """Load YOLO detection model."""
    model = YOLO(model_path)
    return model

def Safety_frame(frame, model, classnames, threshold=50):
    """Detect objects in a single frame and annotate with bounding boxes."""
    results = model(frame, stream=True, verbose=False)

    for info in results:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if len(classnames) < 4 and classnames[Class] == 'awake':
                pass
            elif classnames[Class] == 'Helmet' or classnames[Class] == 'Safty-Vest':
                pass
            elif confidence > threshold:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1, y1 - 10],
                                   scale=1, thickness=2, colorR=(0, 0, 255))
    
    return frame

def ObjectPredictor():
    """Process video frames for object detection."""
    args = parse_arguments()
    video_path = args.get("video", None)

    helmet_vest_model_path = r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt'
    drowsy_model_path = r'C:\Users\rewan\Downloads\GP\Graduation-Project\Awakeness_Detection\best.pt'
    
    helmet_vest_classnames =['fall', 'Safty-Vest', 'Helmet', 'without_Helmet', 'without_Safty-Vest']
    drowsy_classnames = ['drowsy', 'awake', 'fainted']
    
    helmet_vest_model = load_model(helmet_vest_model_path)
    drowsy_model = load_model(drowsy_model_path)
    cap = initialize_video_capture(video_path)

    if not cap.isOpened():
        print("Error opening video capture.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame with both models
        frame = Safety_frame(frame, helmet_vest_model, helmet_vest_classnames)
        frame = Safety_frame(frame, drowsy_model, drowsy_classnames)
        
        cv2.imshow("Object Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ObjectPredictor()
