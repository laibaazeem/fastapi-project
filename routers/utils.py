import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from dotenv import load_dotenv
load_dotenv()
import os


def send_email(reciever_email: str,otp_code:int): 

    sender_email = os.getenv("SMTP_EMAIL")
    receiver_email = reciever_email
    password = os.getenv("SMTP_PASSWORD") # Use the generated app password for Gmail
    subject = "Test Email from FastAPI App"
    body = f"your otp code is {otp_code}"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    smtp_server = os.getenv("SMTP_HOST", "smtp.gmail.com") # For Gmail
    port = int(os.getenv("SMTP_PORT", 587)) # TLS port

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.send_message(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def random_integer():
    random_integer = random.randint(100000, 999999)
    return random_integer

 
