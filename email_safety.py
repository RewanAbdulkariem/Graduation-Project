import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread


def send_email(detection_info):
    passw = "hnky vand dubq rbnb"
    from_email = "rewan.khaled21@gmail.com"
    to_email = "rewan.khaled21@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Safety warning!"

    msg.attach(MIMEText(detection_info))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_email, passw)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def send_email_async(message):
    thread = Thread(target=send_email, args=(message,))
    thread.start()

if __name__ == '__main__':
    message = "drowsy worker detected!"
    send_email(message)    