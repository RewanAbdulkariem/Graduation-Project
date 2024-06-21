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
- __Reem Sabry__
- __Habiba Samir__
- __Nada Elsayed__
- __Toqa Ezzatly__
- __Alaa__ []

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

## Desktop Application

#### Purpose
The desktop application serves as the central hub for integrating and managing the various monitoring functionalities deployed in large institutional environments. It provides real-time insights and alerts related to safety, quality inspection, and environmental conditions.

#### Functionality
The application receives and processes data from sensors, cameras, and embedded systems deployed throughout the institution. It aggregates this data to provide comprehensive monitoring and management capabilities.

#### Features
- **Real-time Monitoring:** Displays live feeds and data streams from sensors and cameras.
- **Alerting System:** Notifies administrators instantly upon detecting safety hazards or critical incidents.
- **Data Visualization:** Presents graphical representations and dashboards for intuitive data analysis.
- **User Interface:** Designed with user-friendly controls and interactive elements for ease of use.

#### Technologies Used
- **Programming Language:** Python
- **Framework:** PyQt5 for GUI development
- **Integration:** Communicates with embedded systems via serial communication protocols.

#### Deployment and Maintenance
The application is deployed on desktop computers running Windows 10. It requires minimal system resources and is maintained through periodic updates and bug fixes.

#### Conclusion
The desktop application plays a pivotal role in our project by providing a unified platform for monitoring and ensuring the safety and performance of personnel and assets within large institutional environments.