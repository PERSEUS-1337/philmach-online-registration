# PhilMach Online Registration

## Owner: Aron Resty Ramillano

### Project Description

**PhilMach Online Registration** is a Python-based registration system developed for **PhilMach 2024**. The system uses Google Forms for participant registration and accesses the Google Sheets API to fetch participant data. Upon registration, participants receive an email containing a unique QR code. This QR code is presented on-site to confirm their attendance and generate a printed copy of their vCard QR code. This vCard QR code can be used to share contact information with exhibitors at the event booths.

### Requirements

- Gmail Account
- Google Forms
- Google Sheets
- Google Sheets API Access via Google Cloud Console
- Python Environment and required packages
- QR Scanners (configured as USB COM devices)
- Thermal Label Printers

### Python Package Dependencies

Here are the Python packages required for this project:

```plaintext
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
Pillow
qrcode
pywin32
python-dotenv
pyserial
```

### Installation

To install the necessary Python packages, use the following command:

#### For QR Scan & Print (Deployed Locally)
```bash
pip install Pillow qrcode pywin32 python-dotenv pyserial
```

#### For GSheets Listener (Deployed on DigitalOcean Droplets)
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client Pillow qrcode python-dotenv
```

### Steps to Deploy

#### For Online Registration

1. **Setup Google Forms and Google Sheets:**
   - Create a Google Form for participant registration.
   - Link the form to a Google Sheet to store responses.

2. **Setup Google Sheets API Access:**
   - Enable the Google Sheets API on your Google Cloud Project.
   - Create and download the necessary credentials file.

3. **Run the `gsheets_listener.py`:**
   - This script monitors the Google Sheet for new registrations.
   - It automatically generates a unique QR code and sends it to participants via email.

4. **Start the GSheets Listener in Background:**
   - Use the `./start_tracking.sh` script to run the listener in the background using `nohup`.
   - To stop the listener, use the `./stop_tracking.sh` script.

#### For On-Site QR Scanning and Printing

1. **Install Prerequisites:**
   - Ensure that all necessary Python packages are installed.
   - Configure the QR Scanner as a **USB COM** device and specify the correct COM port in the `.env` file.

2. **Run the `qr_scanner_printer.py`:**
   - This script handles on-site QR scanning and printing.
   - Set up your thermal label printer as the default printer for seamless operation.

### .env File

Ensure that your `.env` file contains all the necessary environment variables for the application to work correctly. You can refer to the provided `.env.example` file for guidance. Here's a list of expected values to include:

- `GSHEET_CREDS`: Path to your Google Sheets API credentials file.
- `SPREADSHEET_ID`: ID of your Google Sheet containing registration data.
- `RANGE_NAME`: The range in the Google Sheet that will be monitored.
- `SENDER_EMAIL`: Email address used to send registration QR codes.
- `SENDER_PASSWORD`: Password or app-specific password for the sender email.
- `SMTP_SERVER`: SMTP server address (e.g., smtp.gmail.com).
- `SMTP_PORT`: SMTP port (usually 587 for TLS).
- `CSV_FILE_PATH`: File path to store backup CSV data.
- `INTERVAL_SECONDS`: Interval for checking the Google Sheet for changes.
- `COM_PORT`: COM port for the USB COM scanner device.
- `MODE`: Application mode (e.g., `dev` or `prod`).

### Application Flow

1. **Registration via Google Forms:**
   - Participants register by filling out the form.
   - The data is automatically saved in the linked Google Sheet.

2. **Automated QR Code Issuance:**
   - The `gsheets_listener.py` script monitors the Google Sheet for new entries.
   - When a new registration is detected, a unique QR code is generated and emailed to the participant.

3. **On-Site Check-In:**
   - Participants present their unique registration QR code upon arrival at the event.
   - The QR code is scanned on-site to confirm their attendance.
   - After scanning, participants receive a printed vCard QR code containing their contact information.

4. **Sharing Contact Information:**
   - Participants use their vCard QR codes to share contact information with exhibitors at the event booths.

### Additional Notes

- Ensure that your QR scanner is configured as a **USB COM** device. Verify the correct COM port and update the `.env` file accordingly.
- Use the provided `./start_tracking.sh` and `./stop_tracking.sh` scripts to manage the `gsheets_listener.py` process in the background with `nohup`.

---

This project is licensed under the [MIT License](LICENSE). Contributions and feedback are welcome!