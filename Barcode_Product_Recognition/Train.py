from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("yolov8n.pt")  # build a new model from scratch

    # Use the model
    model.train(data="config.yaml", epochs=50, amp=False)  # train the model
