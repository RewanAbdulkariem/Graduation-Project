import os, sys
import cv2
import cvzone
import math
import argparse
from ultralytics import YOLO
from time import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from email_safety import send_email_async

previous_detection = None
last_email_time = 0
email_interval = 60
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

def Safety_frame(frame, model, classnames, threshold=50):
    """Detect objects in a single frame and annotate with bounding boxes."""
    global previous_detection, last_email_time

    results = model(frame, stream=True, verbose=False)

    for info in results:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if len(classnames) < 4 and classnames[Class] == 'Awake':
                pass
            elif classnames[Class] == 'Helmet' or classnames[Class] == 'Safty-Vest':
                pass
            elif confidence > threshold:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%',[x1 + 8, y1 + 80],
                                   scale=2, thickness=3, colorR=(0, 0, 0))
                current_detection = classnames[Class]
                if current_detection != previous_detection:
                    current_time = time()
                    if current_time - last_email_time >= email_interval:
                        send_email_async(f"WARNING: {classnames[Class]} detected with {confidence}% confidence!", frame)
                        last_email_time = current_time
                previous_detection = current_detection
    return frame

def ObjectPredictor():
    """Process video frames for object detection."""
    args = parse_arguments()
    video_path = args.get("video", None)

    helmet_vest_model_path = r'C:\Users\rewan\Downloads\GP\Graduation-Project\VestHelmet_Detection\best.pt'
    drowsy_model_path = r'C:\Users\rewan\Downloads\GP\Graduation-Project\Awakeness_Detection\best.pt'
    
    helmet_vest_classnames =['Fall', 'Safty-Vest', 'Helmet', 'Without_Helmet', 'without_Safty-Vest']
    drowsy_classnames = ['Drowsy', 'Awake', 'Fainted']
    
    helmet_vest_model = YOLO(helmet_vest_model_path)
    drowsy_model = YOLO(drowsy_model_path)
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
