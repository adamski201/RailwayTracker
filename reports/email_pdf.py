import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from boto3 import client
from dotenv import load_dotenv


def generate_email_object(subject: str, body: str, attachment_file_path: str):

    msg = MIMEMultipart()
    msg["Subject"] = "DOES THIS WORK - REPORT SUMMARY"
    msg.attach(MIMEText(
        "Attached to this email is a report on performance statistics for operators."))

    file = MIMEApplication(
        open("test.pdf", "rb").read(),
        name=os.path.basename("test.pdf"))

    file['Content-Disposition'] = f'attachment; filename="{os.path.basename("test.pdf")}"'

    msg.attach(file)

    return msg


email_subject = "DOES THIS WORK - REPORT SUMMARY"
email_text = "Attached to this email is a report on performance statistics for operators."
attachment_file_path = "test.pdf"

email_object = generate_email_object(
    email_subject, email_text, attachment_file_path)

print(type(email_object))


def send_email(email: MIMEMultipart):

    ses_client = client("ses",
                        region_name="eu-west-2",
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    ses_client.send_raw_email(
        Source='trainee.isaac.schaessens.coleman@sigmalabs.co.uk',
        Destinations=[
            'trainee.isaac.schaessens.coleman@sigmalabs.co.uk',
        ],
        RawMessage={
            'Data': email.as_string()
        }
    )


if __name__ == "__main__":

    load_dotenv()

    email_subject = "DOES THIS WORK - REPORT SUMMARY"
    email_text = "Attached to this email is a report on performance statistics for operators."
    attachment_file_path = "test.pdf"

    email_object = generate_email_object(
        email_subject, email_text, attachment_file_path)

    send_email(email_object)
