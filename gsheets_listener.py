# gsheets_listener.py
# Listens from the GSheets for any updates regarding new registration entries every 5 seconds
# Generates QR code based on the information inputted by new entries
# Sends QR code via email to the registrants using their entered emails

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import qrcode

from dotenv import load_dotenv
import csv
import logging
import time
import os

# Load .env file
load_dotenv()

# Access environment variables
secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

# Load the service account credentials
creds = Credentials.from_service_account_file(os.getenv("GSHEET_CREDS"))

# Build the service
sheets_api = build("sheets", "v4", credentials=creds)
gmail_api = build('gmail', 'v1', credentials=creds)

# Spreadsheet ID and Range
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME")

# Ensure directories exist
os.makedirs("codes", exist_ok=True)
os.makedirs("images", exist_ok=True)

# Setup Backup Database (CSV)
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

# Set time interval of checking gsheet
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS"))

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def save_to_csv(data, file_path):
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)


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


def detect_changes(previous_data, new_data):
    changes_detected = False
    new_entries = []

    # Check if new rows have been added
    if len(new_data) > len(previous_data):
        changes_detected = True
        new_entries = new_data[len(previous_data):]

    return changes_detected, new_entries


def generate_qr_code_with_basic_info(first_name, last_name, email, number, company):
    # Create a string with basic information, e.g., "FirstName;LastName;Email;Number;Company"
    basic_info = f"{first_name};{last_name};{email};{number};{company}"

    # Create QR code containing the basic information
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(basic_info)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    # Ensure the "codes" directory exists
    os.makedirs("codes", exist_ok=True)

    # Save the QR code in the "codes" directory
    filename = os.path.join("codes", f"{first_name}_{last_name}_qr.png")
    img.save(filename)
    print(f"QR code generated and saved as {filename}")
    return filename


def send_email(to_email, last_name, qr_filename):
    print("Attempting to send email...")

    from_email = sender_email  # Your Gmail address
    password = sender_password  # Your Gmail App Password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For TLS

    subject = f"PhilMach 2024 Registration Confirmed - {last_name.upper()}"
    body = (f"Thank you for registering, Ms./Mr. {last_name}.\n\n"
            f"Attached is your unique registration QR code.\n"
            f"Please present this QR code on the day of your attendance to receive your booth QR codes.")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

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
        print(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(
            "SMTP Authentication Error: Could not log in to the SMTP server. Check your username and password."
        )
    except smtplib.SMTPRecipientsRefused as e:
        print(
            f"SMTP Recipients Refused: The recipient {to_email} was rejected by the server."
        )
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main loop to periodically fetch data
previous_data = get_sheet_data(SPREADSHEET_ID, RANGE_NAME)


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
                    email, first_name, last_name, number, company = entry[1:6]  # Adjust indices as per the form fields

                    qr_filename = generate_qr_code_with_basic_info(
                        first_name, last_name, email, number, company
                    )

                    # Log that an email is being sent
                    logging.info(
                        f"Sending email to {email} with attached QR code: {qr_filename}"
                    )

                    # Send the email
                    send_email(email, last_name, qr_filename)

                # Update the previous data only if changes are detected
                previous_data = new_data

                # Save the updated data to CSV
                save_to_csv(previous_data, CSV_FILE_PATH)
            else:
                # Log when no changes are detected
                logging.info("No changes detected.")

    except KeyboardInterrupt:
        logging.info("Interrupted by user. Shutting down gracefully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}. Shutting down gracefully.")


if __name__ == "__main__":
    logging.info("Starting monitoring...")
    monitor_changes()
    logging.info("Monitoring stopped.")
