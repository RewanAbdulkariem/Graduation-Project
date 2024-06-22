import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from threading import Thread
from cv2 import imencode

def send_email(detection_info, frame):
    # Convert the frame (OpenCV image) to a JPEG image
    if frame != None:
        ret, buffer = imencode('.jpg', frame)
        if not ret:
            print("Error: Could not convert frame to JPEG")
            return

    passw = "hnky vand dubq rbnb"
    from_email = "rewan.khaled21@gmail.com"
    to_email = "rewan.khaled21@gmail.com"

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Safety warning!"

    # Attach the body text
    text = MIMEText(detection_info, "plain")
    msg.attach(text)
    if frame != None:
        # Attach the image
        image = MIMEImage(buffer.tobytes(), name="frame.jpg")
        msg.attach(image)

    # Send the email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_email, passw)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def send_email_async(message, frame):
    thread = Thread(target=send_email, args=(message,frame))
    thread.start()

if __name__ == '__main__':
    message = "drowsy worker detected!"
    send_email(message, None)    