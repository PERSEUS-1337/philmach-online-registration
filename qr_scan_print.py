from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image, ImageDraw, ImageFont, ImageWin
from pyzbar.pyzbar import decode
import hashlib
import qrcode
import cv2

import win32print
import win32api
import win32ui

import time
import smtplib
import os

# Load the service account credentials
creds = Credentials.from_service_account_file(
    "..//philmach-qr-registration-3e8120628a48.json"
)

# Build the service
sheets_api = build("sheets", "v4", credentials=creds)
SPREADSHEET_ID = "1059XcoaLZkbi-tS8j6lClfxl29gHkshdxPoS-a3Ey_I"


# Function to print the QR code image using the default Windows printer
# def print_qr_code(filename):
#     # Define the desired size in millimeters and convert to pixels
#     desired_width_mm = 70
#     desired_height_mm = 30
#     dpi = 5  # Commonly used DPI for printing
#     width_px = int(desired_width_mm * dpi / 25.4)  # Convert mm to inches and then to pixels
#     height_px = int(desired_height_mm * dpi / 25.4)
#
#     # Get the default printer name
#     printer_name = win32print.GetDefaultPrinter()
#
#     # Open the image file
#     img = Image.open(filename)
#     img = img.convert('RGB')  # Ensure the image is in RGB mode
#
#     # Resize the image to the desired size
#     img = img.resize((width_px, height_px), Image.LANCZOS)
#
#     # Start the print job
#     hdc = win32ui.CreateDC()
#     hdc.CreatePrinterDC(printer_name)
#     hdc.StartDoc(filename)
#     hdc.StartPage()
#
#     # Get the printable area of the printer
#     printer_width = hdc.GetDeviceCaps(8)  # HORZRES
#     printer_height = hdc.GetDeviceCaps(10)  # VERTRES
#
#     # Determine the position where the image should be printed
#     x_position = (printer_width - width_px) // 2
#     y_position = (printer_height - height_px) // 2
#
#     # Convert the image to a DIB (Device Independent Bitmap) and draw it on the printer device context
#     dib = ImageWin.Dib(img)
#     dib.draw(hdc.GetHandleOutput(), (x_position, y_position, x_position + width_px, y_position + height_px))
#
#     # End the page and the print job
#     hdc.EndPage()
#     hdc.EndDoc()
#
#     # Clean up
#     hdc.DeleteDC()


# Function to print the QR code image using the default Windows printer
def print_qr_code(filename):
    # Define the label size in millimeters
    label_width_mm = 70
    label_height_mm = 50

    # Define the QR code size in millimeters
    qr_width_mm = 45
    qr_height_mm = 45

    # Convert millimeters to pixels using a typical DPI for thermal printers
    dpi = 175  # Assuming a 300 DPI printer
    label_width_px = int(
        label_width_mm * dpi / 25.4
    )  # Convert mm to inches and then to pixels
    label_height_px = int(label_height_mm * dpi / 25.4)
    qr_width_px = int(qr_width_mm * dpi / 25.4)
    qr_height_px = int(qr_height_mm * dpi / 25.4)

    # Get the default printer name
    printer_name = win32print.GetDefaultPrinter()

    # Open the image file
    img = Image.open(filename)
    img = img.convert("RGB")  # Ensure the image is in RGB mode

    # Resize the QR code image to the desired QR code size
    img = img.resize((qr_width_px, qr_height_px), Image.LANCZOS)

    # Start the print job
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc(filename)
    hdc.StartPage()

    # Get the printable area of the printer
    printer_width = hdc.GetDeviceCaps(8)  # HORZRES
    printer_height = hdc.GetDeviceCaps(10)  # VERTRES

    # Calculate the position to center the QR code within the label
    x_position = (label_width_px - qr_width_px) // 2
    y_position = (label_height_px - qr_height_px) // 2

    # Convert the image to a DIB (Device Independent Bitmap) and draw it on the printer device context
    dib = ImageWin.Dib(img)
    dib.draw(
        hdc.GetHandleOutput(),
        (x_position, y_position, x_position + qr_width_px, y_position + qr_height_px),
    )

    # End the page and the print job
    hdc.EndPage()
    hdc.EndDoc()

    # Clean up
    hdc.DeleteDC()


def print_qr_code_with_details(
    qr_filename, first_name, last_name, email, number, company
):
    full_name = f"{first_name} {last_name}"

    # Define the desired size in millimeters and convert to pixels
    desired_width_mm = 750  # Increased width for more space
    desired_height_mm = 300  # Height remains the same
    dpi = 72  # Commonly used DPI for printing
    width_px = int(
        desired_width_mm * dpi / 25.4
    )  # Convert mm to inches and then to pixels
    height_px = int(desired_height_mm * dpi / 25.4)

    # Create a new blank image for the composite
    composite_img = Image.new("RGB", (width_px, height_px), color="white")

    # Load the QR code image
    qr_img = Image.open(qr_filename)
    qr_img = qr_img.convert("RGB")  # Ensure the image is in RGB mode

    # Define sizes for the QR code and text section
    qr_width_mm = desired_height_mm  # Define the QR code width
    qr_height_mm = desired_height_mm  # Define the QR code height
    qr_width_px = int(qr_width_mm * dpi / 25.4)
    qr_height_px = int(qr_height_mm * dpi / 25.4)

    # Resize the QR code image to fit its defined size
    qr_img = qr_img.resize((qr_width_px, qr_height_px), Image.LANCZOS)

    # Paste the QR code image into the composite
    composite_img.paste(qr_img, (0, 0))

    # Draw the user details on the right side
    draw = ImageDraw.Draw(composite_img)

    # Define font size
    font_size = (
        qr_height_px // 13
    )  # Make the font size proportional to the QR code height
    font = ImageFont.truetype(
        "arial.ttf", font_size
    )  # You can specify a different font if needed

    # Define text positions and content
    details_x = qr_width_px + 30  # 30 pixels padding from QR code
    details_y = 10
    line_spacing = font_size * 1.5  # Adjust spacing based on font size

    # Prepare text content
    text_lines = [
        f"Full Name: {full_name}",
        f"Email: {email}",
        f"Number: {number}",
        f"Company: {company}",
    ]

    # Calculate the total height required for the text block
    total_text_height = len(text_lines) * line_spacing

    # Adjust text position to center vertically
    details_y = (qr_height_px - total_text_height) // 2

    # Add text to the image
    for i, line in enumerate(text_lines):
        draw.text(
            (details_x, details_y + i * line_spacing), line, font=font, fill="black"
        )

    # Save the composite image
    composite_filename = qr_filename.replace(".png", "_composite.png")
    composite_img.save(composite_filename)
    print(f"Composite image saved as {composite_filename}")

    # Start the print job
    printer_name = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc(composite_filename)
    hdc.StartPage()

    # Get the printable area of the printer
    printer_width = hdc.GetDeviceCaps(8)  # HORZRES
    printer_height = hdc.GetDeviceCaps(10)  # VERTRES

    # Determine the position where the image should be printed
    x_position = (printer_width - width_px) // 2
    y_position = (printer_height - height_px) // 2

    # Convert the image to a DIB (Device Independent Bitmap) and draw it on the printer device context
    dib = ImageWin.Dib(composite_img)
    dib.draw(
        hdc.GetHandleOutput(),
        (x_position, y_position, x_position + width_px, y_position + height_px),
    )

    # End the page and the print job
    hdc.EndPage()
    hdc.EndDoc()

    # Clean up
    hdc.DeleteDC()


# Function to handle keyboard input of hash and decoding
def decode_qr():
    hash_value = input("Enter the QR hash: ")
    user_info = lookup_user_info(hash_value)

    if user_info:
        # Generate a new QR code with the user's details
        qr_filename = generate_vcard_qr(*user_info)
        print(f"Generated QR Code with user details: {qr_filename}")

        # Print the QR code
        print_qr_code_with_details(qr_filename, *user_info)


def decode_qr_to_vcard():
    # Assume qr_data is in the format "FirstName;LastName;Email;Number;Company"
    qr_string = input("Enter the QR hash: ")
    try:
        # Split the QR string into components
        first_name, last_name, email, number, company = qr_string.split(";")

        # Generate the vCard data (no indentation)
        vcard_data = f"""
BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name};;;
EMAIL:{email}
TEL:{number}
ORG:{company}
END:VCARD
        """.strip()

        print("Generated vCard from QR Data:")
        print(vcard_data)

        # Generate a QR code containing the vCard data
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=1,
        )
        qr.add_data(vcard_data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        # Ensure the "vcard_qr_codes" directory exists
        os.makedirs("vcard_qr_codes", exist_ok=True)

        # Save the QR code as a PNG file
        qr_filename = os.path.join(
            "vcard_qr_codes", f"{first_name}_{last_name}_vcard_qr.png"
        )
        img.save(qr_filename)
        print(f"vCard QR code saved as {qr_filename}")

        return qr_filename

    except ValueError:
        print("Error: Invalid QR data format.")
        return None


# Main menu to choose between camera or keyboard input
def main_menu():
    while True:
        print("QR Code Processing System")
        print("1. Start QR Code Reader (Camera)")
        print("2. Input QR Hash Manually")
        print("3. Input QR Hash Manually & Print")
        print("q. Quit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            read_qr_code()
        elif choice == "2":
            decode_qr_to_vcard()
        elif choice == "3":
            filename = decode_qr_to_vcard()
            print_qr_code(filename)
        elif choice == "q":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


# Start the main menu
if __name__ == "__main__":
    main_menu()
