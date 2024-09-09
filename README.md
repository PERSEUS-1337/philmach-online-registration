# philmach_online_registration

## Owner: Aron Resty Ramillano

### Project Description

**PhilMach Online Registration** is a Python-based Registration System developed for **PhilMach 2024**. It utilizes Google Forms for participant registration and accesses the Google Sheets API to fetch participant data. Upon registration, participants receive an email containing a unique QR code. This QR code can be scanned on-site to register their attendance and generate a printed copy of their vCard QR code, which they can attach to their IDs. This vCard QR code serves as their means of "attendance" at each booth during the event.

### Requirements

- Gmail Account
- Google Forms
- Google Sheets
- GSheets API Access via Google Workspace
- Python Environment and its packages for the code
- QR Scanners
- Thermal Label Printers

### Python Package Dependencies

Here are the Python packages required for this project:

```plaintext
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
Pillow
pyzbar
qrcode
opencv-python-headless
pywin32
python-dotenv
```

### Installation

To install the necessary Python packages, use the following command:

#### For qr_scan_print (deployed locally)
```bash
pip install Pillow qrcode pywin32 python-dotenv
```

#### For gsheets_listener (deployed on DigitalOcean Droplets)
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client Pillow pyzbar qrcode opencv-python-headless pywin32 python-dotenv
```
### Steps to Deploy

#### For Online Registration

1. **Setup Google Forms and Google Sheets:**
   - Create a Google Form for participant registration.
   - Link the form to a Google Sheet to store responses.

2. **Setup GSheets API Access:**
   - Enable the Google Sheets API on your Google Cloud Project.
   - Create and download the necessary credentials file.

3. **Run the `gsheets_tracker.py`:**
   - This script will monitor the Google Sheet for new registrations.
   - It will automatically send an email with a unique QR code to each new participant.

#### For On-Site QR Scanning and Printing

1. **Install Prerequisites:**
   - Ensure that all necessary Python packages are installed.
   - Setup the QR Scanner as a USB HID to act as a keyboard, outputting the decoded string from the QR code.

2. **Run the `qr_scanner_printer.py`:**
   - This program will handle the on-site QR scanning and printing.
   - Make sure the Thermal Label Printer is set as the default printer to automatically print the outputs.

### Additional Notes

- Ensure that the QR scanner is correctly configured to function as a keyboard HID device.
- The system is designed to work seamlessly with thermal label printers for quick and efficient ID attachment printing.

---

This project is licensed under the [MIT License](LICENSE). Contributions and feedback are welcome!