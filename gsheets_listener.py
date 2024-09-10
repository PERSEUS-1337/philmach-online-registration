# gsheets_listener.py
# Listens for updates in Google Sheets every 5 seconds, generates QR codes based on new entries,
# and sends QR codes via email to registrants using their entered emails.

import os
import time
import logging
import csv
from dotenv import load_dotenv

import qrcode
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from helpers import generate_hash, decode_hash, clean_file

# Load environment variables from .env file
load_dotenv()

# Access environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS"))
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# Load the service account credentials for Google Sheets and Gmail
creds = Credentials.from_service_account_file(os.getenv("GSHEET_CREDS"))
sheets_api = build("sheets", "v4", credentials=creds)
gmail_api = build("gmail", "v1", credentials=creds)

# Ensure necessary directories exist
os.makedirs("codes", exist_ok=True)

# Set up backup database (CSV)
if not os.path.exists(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["First Name", "Last Name", "Email", "Number", "Company"])

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Code execution starts below
def save_to_csv(data, file_path):
    with open(file_path, mode="w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)


def load_from_csv(file_path):
    if not os.path.exists(file_path):
        return []  # Return an empty list if the file doesn't exist

    with open(file_path, mode="r", newline="") as file:
        reader = csv.reader(file)
        return list(reader)


def get_sheet_data(spreadsheet_id, range_name):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


def detect_changes(prev_data, new_data):
    changes_detected = False
    new_entries = []

    # Check if new rows have been added
    if len(new_data) > len(prev_data):
        changes_detected = True
        new_entries = new_data[len(prev_data):]

    return changes_detected, new_entries


def generate_qr_code_with_user_info(first_name, last_name, email, number, company):
    # Create a string with basic information, e.g., "FirstName;LastName;Email;Number;Company"
    user_info = f"{first_name};{last_name};{email};{number};{company}"

    # Generate a consistent hash based on user info
    user_hash = generate_hash(user_info)

    # Create QR code containing the hashed information
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(user_hash)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    # Save the QR code in the "codes" directory
    filename = os.path.join("codes", f"{first_name}_{last_name}_qr.png")
    img.save(filename)
    logging.info(f"QR code generated and saved as {filename}")
    return filename


def send_email(to_email, last_name, qr_filename):
    logging.info(f"Attempting to send email to {to_email}.")

    from_email = SENDER_EMAIL  # Your Gmail address
    password = SENDER_PASSWORD  # Your Gmail App Password
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT  # For TLS

    subject = f"PhilMach 2024 Registration Confirmed - {last_name.upper()}"

    body = (
        f"Dear Ms./Mr. {last_name},<br><br>"
        f"Thank you for registering for <b>PHILMACH</b> – the <b>Philippines Machinery Exhibition</b>, happening from "
        f"<b>October 17-19, 2024</b>, at the <b>SMX Convention Center</b> near Mall of Asia, in Pasay, "
        f"Metro Manila.<br><br>"
        f"Attached to this email is your unique registration QR code. Please present this QR code upon your arrival "
        f"at the venue. Our team will scan it to generate your personalized contact QR code, which you can use to "
        f"easily share your details with exhibitors throughout the convention.<br><br>"
        f"We look forward to seeing you at the <b>12th PHILMACH 2024</b>!<br><br>"
        f"Best regards,<br>"
        f"The 12th PHILMACH 2024 Team."
    )

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Attach the vCard QR code
    with open(qr_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(qr_filename)}",
    )
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {to_email}.")

    except smtplib.SMTPAuthenticationError as e:
        logging.error(
            f"SMTP Authentication Error: Could not log in to the SMTP server. "
            f"Check your username ({from_email}) and password."
        )
    except smtplib.SMTPRecipientsRefused as e:
        logging.error(
            f"SMTP Recipients Refused: The recipient {to_email} was rejected by the server."
        )
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def monitor_changes():
    # Load previous data from CSV
    previous_data = load_from_csv(CSV_FILE_PATH)

    try:
        while True:
            interval = INTERVAL_SECONDS  # Seconds
            time.sleep(interval)

            # Log the time of the check
            logging.info("Checking for changes in the sheet...")

            new_data = get_sheet_data(SPREADSHEET_ID, RANGE_NAME)
            changes_detected, new_entries = detect_changes(previous_data, new_data)

            if changes_detected:
                logging.info(f"Changes detected: {len(new_entries)} new entries found.")

                for i, entry in enumerate(new_entries):
                    email, first_name, last_name, number, company = entry[
                        1:6
                    ]  # Adjust indices as per the form fields

                    qr_filename = generate_qr_code_with_user_info(
                        first_name, last_name, email, number, company
                    )

                    # Send the email
                    send_email(email, last_name, qr_filename)

                    # Delete the generated files
                    clean_file(qr_filename)

                # Update the previous data only if changes are detected
                previous_data = new_data

                # Save the updated data to CSV
                save_to_csv(previous_data, CSV_FILE_PATH)
            else:
                # Log when no changes are detected
                logging.info("No changes detected.")

    except KeyboardInterrupt:
        logging.critical("Interrupted by user. Shutting down gracefully.")
    except Exception as e:
        logging.critical(f"An error occurred: {e}. Shutting down gracefully.")


if __name__ == "__main__":
    logging.info("Starting monitoring...")
    monitor_changes()
    logging.info("Monitoring stopped.")
