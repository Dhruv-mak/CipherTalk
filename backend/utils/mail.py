import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dotenv import load_dotenv
import pdb
import os

load_dotenv()

env = Environment(
    loader=FileSystemLoader('utils/email_templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_email(receiver_email, subject, html_content):
    msg = MIMEMultipart()
    msg['From'] = "nmikealson@dmakwana.tech"
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.login(os.getenv("MAILTRAP_SMTP_USER"), os.getenv("MAILTRAP_SMTP_PASS"))
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

def email_verification_content(username, verification_url):
    template = env.get_template('email_verification.html')
    return template.render(username=username, verification_url=verification_url)

def forgot_password_content(username, reset_url):
    template = env.get_template('forgot_password.html')
    return template.render(username=username, reset_url=reset_url)