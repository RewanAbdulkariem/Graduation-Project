# Real-time Performance and Safety Monitoring in Large Institutions
## Introduction
This project aims to provide real-time monitoring solutions for performance and safety in large institutions using computer vision and IoT technologies. It offers functionalities ranging from object detection and classification to environmental monitoring through sensor data.

## Features
- Safety Monitoring: Detection of safety violations such as improper safety gear usage (helmets, vests) and drowsiness detection.
- Crowd Detection: Real-time tracking and analysis of crowd dynamics within institutional environments.
- Defect Detection and Classification: Identification and classification of defects in manufactured goods using computer vision techniques.
- Barcode Product Recognition: Automatic recognition and decoding of barcodes for inventory management.
- Fire Detection: Early detection of fire hazards using image processing techniques.

## Team Members
Reem Sabry
Habiba Samir
Nada Elsayed
Toqa Ezzatly
Alaa []

## Dependencies
- Python 3
- PyQt5
- OpenCV
- TensorFlow, PyTorch, or other specific libraries for deep learning models
- Other dependencies as listed in respective module directories

## Installation
Clone the repository:

```bash
git clone https://github.com/[username]/Real-time-Performance-Safety-Monitoring.git
cd Real-time-Performance-Safety-Monitoring
```

## Usage
1. Run the Main Application:

```bash
python GUI.py
```
- Ensure to edit paths in GUI.py file 
- Select the appropriate model and start video processing.
- Use tabs to switch between functionalities (Safety Monitoring, Crowd Detection, Defect Detection, etc.).
2. Serial Communication Setup:
- Ensure the correct COM port is specified in SerialThread (Serial.py).
- Modify baud rate settings if necessary.
3. Email Configuration:
- Modify the email sender and receiver addresses in email_safety.py.
- Use a valid Gmail account with less secure apps enabled or app-specific password.
## Sending Email Notifications
- The application includes functionality to send email notifications when safety violations are detected.
- Ensure email configuration is correctly set up in email_safety.py for sending notifications.
- Notifications are sent for safety violations such as improper safety gear usage and drowsiness detection.