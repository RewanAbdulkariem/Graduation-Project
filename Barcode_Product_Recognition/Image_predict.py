import os
import cv2
from ultralytics import YOLO
from pyzbar.pyzbar import decode
import json
import argparse


def ImagePredictor(image_path):
    # Load YOLO model
    model_path = os.path.join('.', 'last.pt')
    model = YOLO(model_path)

    # Set detection threshold
    threshold = 0.5

    # Read input image
    img = cv2.imread(image_path)

    # Predict using YOLO
    results = model(image_path)[0] # predict on an image
    
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        # Crop the detected region
        croped_img = img[int(y1)-50:int(y2)+50, int(x1)-50:int(x2)+50]
        text = " "
        try:
            # Decode barcode from the cropped image
            barcode = decode(croped_img)[0]
            barcode = barcode.data.decode('utf-8')

            # Check if the barcode exists in the product database
            with open(os.path.join('.', 'products.json'), "r") as products:
                data = json.load(products)
                if barcode in data:
                    text = data[barcode]
        except:
            print("Can't be decoded")

        if score > threshold:
            # Draw bounding box and display product name
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cv2.putText(img, text, (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
    # Display the processed image   
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--image', help='path to the input image file')
    args = vars(parser.parse_args())

    # Call main function with the specified image path
    ImagePredictor(args["image"])