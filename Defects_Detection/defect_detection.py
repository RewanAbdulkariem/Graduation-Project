import cv2
from ultralytics import YOLO
import os
def defectframe(frame, model):
    results = model(frame)
    
    annotated_frame = results[0].plot()
    return annotated_frame

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the desired directory structure
    model_path = os.path.join(script_dir, 'defectdetection.pt')

    model = YOLO(model_path)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        exit()

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        annotated_frame = defectframe(frame, model)

        cv2.imshow('Defects Detection', annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
