import os
import cv2
from ultralytics import YOLO
from pyzbar.pyzbar import decode
import argparse
import json

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

def load_barcode_model(model_path):
    """Load YOLO object detection model."""
    model = YOLO(model_path)
    return model

def Barcodeframe(frame, model, threshold=0.5):
    """Perform object detection and barcode decoding on a single frame."""
    results = model(frame, verbose=False)[0]
    
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        cropped_frame = frame[int(y1)-50:int(y2)+50, int(x1)-50:int(x2)+50]
        text = "Not Found"
        
        try:
            barcode = decode(cropped_frame)[0]
            barcode = barcode.data.decode('utf-8')
            
            with open('products.json', "r") as products:
                data = json.load(products)
                if barcode in data:
                    text = data[barcode]
        except:
            pass

        if score > threshold:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cv2.putText(frame, text.upper(), (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
    
    return frame

def VideoPredictor():
    """Main function to process video frames."""
    args = parse_arguments()
    video_path = args.get("video", None)
    
    model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')
    model = load_barcode_model(model_path)
    
    cap = initialize_video_capture(video_path)
    if not cap.isOpened():
        print("Error opening video capture.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = Barcodeframe(frame, model)
        cv2.imshow("Frame", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    VideoPredictor()
