import smtplib
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SENDER_EMAIL_ADDRESS = os.getenv('SENDER_EMAIL_ADDRESS')
SENDER_EMAIL_PASSWORD = os.getenv('SENDER_EMAIL_PASSWORD')
RECEIVER_EMAIL_ADDRESS = os.getenv('RECEIVER_EMAIL_ADDRESS')

def float_this(num):
    try:
        return float(num)
    except:
        return 0.0

def send_email(body):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        server.login(SENDER_EMAIL_ADDRESS, SENDER_EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL_ADDRESS, RECEIVER_EMAIL_ADDRESS, body)
