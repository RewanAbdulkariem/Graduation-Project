import cv2
import math
from ultralytics import YOLO

def defectclassframe(frame, model, threshold=50):
    # Perform inference on the frame
    results = model(frame, stream=True, verbose=False)

    for info in results:
        boxes = info.boxes
        for box in boxes:
            conf = box.conf[0]
            conf = math.ceil(conf * 100)
            cls = int(box.cls[0])
            if conf >= threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = f'{model.names[cls]} {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

if __name__ == "__main__":
    model = YOLO(r"C:\Users\rewan\Downloads\GP\Graduation-Project\Defects_Classification\defectClassification.pt")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        exit()

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        annotated_frame = defectclassframe(frame, model)

        cv2.imshow('Defects class', annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
