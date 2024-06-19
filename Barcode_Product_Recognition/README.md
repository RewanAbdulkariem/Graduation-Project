# Barcode Product Recognition
Real-time barcode detection and product recognition using YOLO object detection and PyZBar. Includes image and video processing scripts for identifying products from barcodes.

## Features
**Object Detection**: Utilizes YOLO (You Only Look Once) for accurate and efficient object localization.
**Barcode Decoding**: Uses PyZBar library to decode barcode information from cropped regions of interest in images or video frames.
**Product Recognition**: Matches decoded barcode information against a predefined product database to identify products.
**Real-time Processing**: Supports live video processing for instant product recognition.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/Barcode-Product-Recognition.git
```

## Usage
### Image Processing
To process a single image for barcode detection and product recognition, run:
```bash
python Image_predict.py -i path_to_image.jpg
```
Replace path_to_image.jpg with the path to your input image.

### Real-time Video Processing
To process live video from a camera or a video file, run:
```bash
python Video_predict.py -v path_to_video.mp4
```
Replace path_to_video.mp4 with the path to your video file. If no video path is provided, the script will use the default camera.
## File Structure
```bash
Barcode-Product-Recognition/
│
├── Image_predict.py
├── Video_predict.py
└── products.json
```
1. __Image_predict.py__: Script for barcode detection and product recognition on a single image.
2. __Video_predict.py__: Script for real-time video processing with barcode detection and product recognition.
3. __products.json__: JSON file containing product information mapped by barcode.