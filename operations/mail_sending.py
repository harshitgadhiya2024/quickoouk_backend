import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_SERVER = "smtp.gmail.com"  # Change if using Outlook, Yahoo, etc.
SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
EMAIL_ADDRESS = "gadhiyaharshit2023@gmail.com"
EMAIL_PASSWORD = "bsxlmkiufmydlrhy"  # Use app password for Gmail

class emailOperation():

    def __init__(self):
        pass

    # Function to Send HTML Email
    def send_email(self, to_email, subject, html_body):
        try:
            # Create Email Message
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))  # Set as HTML

            # Connect to SMTP Server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            print("Email sent successfully!")

            return "sent"

        except Exception as e:
            print(f"{datetime.utcnow()}: Failed to send email: {e}")

    # Function to Send Email with Attachment
    def send_email_with_attechment(self, to_email, subject, html_body, attachment_paths):
        try:
            # Create Email Message
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to_email
            msg["Subject"] = subject

            # Attach HTML Body
            msg.attach(MIMEText(html_body, "html"))

            # Attach File
            for attachment_path in attachment_paths:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                msg.attach(part)

            # Connect to SMTP Server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            print("Email sent successfully!")

            return "sent"

        except Exception as e:
            print(f"{datetime.utcnow()}: Failed to send email with attechment: {str(e)}")

