import cv2
import argparse
import pandas as pd
from ultralytics import YOLO
import cvzone
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from email_safety import send_email_async
from time import time

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

def load_class_list(class_file_path):
    """Load class list from file."""
    class_list = []
    with open(class_file_path, "r") as f:
        class_list = f.read().split("\n")
    return class_list

def detect_and_track(frame, model, class_list, tracker):
    """Detect objects in a frame and track them."""
    global last_email_time, email_interval
    results = model.predict(frame)
    if not results:
        return frame

    predictions = results[0].boxes.data.cpu().numpy()
    df = pd.DataFrame(predictions, columns=["x1", "y1", "x2", "y2", "confidence", "class"])

    detections = []
    for _, row in df.iterrows():
        x1, y1, x2, y2, conf, cls = row
        cls = int(cls)
        if 'person' in class_list[cls]:
            detections.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])

    bbox_id = tracker.update(detections)
    person_count = len(bbox_id)
    for bbox in bbox_id:
        x, y, w, h, id = bbox
        cx, cy = int((x + x + w) / 2), int((y + y + h) / 2)
        cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'{id}', (x, y), 1, 2)

    text_size, _ = cv2.getTextSize(f'Persons Detected: {person_count}', cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
    text_w, text_h = text_size
    cv2.rectangle(frame, (0, 30 - text_h - 5), (10 + text_w, 30 + 5), (0,0,0), -1)
    cv2.putText(frame, f'Persons Detected: {person_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)

    current_time = time()
    if current_time - last_email_time >= email_interval:
        if person_count > 20:  # Replace with your desired threshold
            send_email_async(f'WARNING: A crowd of {person_count} people has been detected.', frame)
            last_email_time = current_time
    return frame

def CrowdDetector():
    """Process video frames for crowd detection."""
    args = parse_arguments()
    video_path = args.get("video", None)


    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the desired directory structure
    model_path = os.path.join(script_dir, 'yolov8s.pt')

    class_file_path =os.path.join(script_dir, 'coco.txt')

    class_list = load_class_list(class_file_path)
    model = YOLO(model_path)
    cap = initialize_video_capture(video_path)
    tracker = Tracker()

    if not cap.isOpened():
        print("Error opening video capture.")
        return

    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        count += 1
        if count % 3 != 0:
            continue

        frame = cv2.resize(frame, (1020, 500))
        processed_frame = detect_and_track(frame, model, class_list, tracker)
        cv2.imshow("Crowd Detection", processed_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # i have issue when i try to import this file outside the folder with this line
    # so i decide to put it here till i find solution for it  
    from tracker import Tracker
    CrowdDetector()
