import os, sys
import cv2
import cvzone
import math
import argparse
from ultralytics import YOLO
from time import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from email_safety import send_email_async

# Global variable to track last email sent time
last_email_sent_time = 0

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

def fireframe(frame, model, threshold=50):
    """Detect fire in a single frame and annotate with bounding boxes."""
    results = model(frame, stream=True, verbose=False)
    classnames = ['fire']
    fire_detected = False
    for info in results:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if confidence > threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100],
                                   scale=3, thickness=3, colorR=(0, 0, 0))
                fire_detected = True
    # Send email if fire detected and not sent within the last 15 minutes
    global last_email_sent_time
    current_time = time()
    if fire_detected and (current_time - last_email_sent_time) >= 900:  # 900 seconds = 15 minutes
        send_email_async("WARNING: Fire detected!",frame)
        last_email_sent_time = current_time  # Update last email sent tim
    return frame

def FirePredictor():
    """Process video frames for fire detection."""
    args = parse_arguments()
    video_path = args.get("video", None)

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the desired directory structure
    model_path = os.path.join(script_dir, 'fire.pt')

    model = YOLO(model_path)
    cap = initialize_video_capture(video_path)

    if not cap.isOpened():
        print("Error opening video capture.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = fireframe(frame, model)
        cv2.imshow("Fire Detection", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    FirePredictor()