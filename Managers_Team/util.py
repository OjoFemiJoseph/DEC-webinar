import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def create_snow_engine(uri):
    """
    Create and return a SQLAlchemy database engine.

    Parameters:
    - uri (str): database connection URI.

    return:
    - engine: SQLAlchemy engine connected to the database.

    Raises:
    - Exception: If there's an error in creating the engine.
    """

    try:
        engine = create_engine(uri)
        return engine
    except SQLAlchemyError as e:
        send_mail(
            {'ojofemijoseph@outlook.com':'Joseph Ojo'},
            f"Failed to create db engine: {str(e)}",
            'Failed')


def send_mail(emailsAddresses, message, subject=None):

    fromaddr = os.getenv('EMAIL_ADDRESS')
    pass_w = os.getenv('EMAIL_PASSWORD')
    
    for toaddr, name in emailsAddresses.items():
        
        msg = MIMEMultipart()
        msg['From'] = "Webinar Pipeline"
        msg['To'] = toaddr
        msg['Subject'] = f"FPL Fixture Pipeline: {subject}"
        body = message
        context = ssl.create_default_context()

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(fromaddr, pass_w)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            print(f"Email sent to {toaddr} ({name})")
