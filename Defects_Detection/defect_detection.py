import cv2
from ultralytics import YOLO

def defectframe(frame, model):
    results = model(frame)
    
    annotated_frame = results[0].plot()
    return annotated_frame

if __name__ == "__main__":
    model = YOLO(r"C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Detection\defectdetection.pt")

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
