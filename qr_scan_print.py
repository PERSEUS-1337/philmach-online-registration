import logging
import os
import time

import qrcode
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin

from helpers import verify_hash, clean_file

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def print_qr_code_with_details(qr_filename, first_name, last_name):
    logging.info(f"Attempting to print vCard QR Code for {first_name} {last_name}.")

    full_name = f"{first_name} {last_name}"
    width_px, height_px = 525, 365  # Define the image size in pixels

    try:
        # Create a new blank image for the composite
        composite_img = Image.new("RGB", (width_px, height_px), color="white")
        qr_img = Image.open(qr_filename).convert("RGB")  # Load and ensure QR image is in RGB mode

        qr_height_px = int(height_px * 3 / 4)
        qr_width_px = qr_height_px  # Keep the QR code square
        qr_img = qr_img.resize((qr_width_px, qr_height_px), Image.LANCZOS)

        qr_x = (width_px - qr_width_px) // 2
        qr_y = height_px - qr_height_px - 15

        composite_img.paste(qr_img, (qr_x, qr_y))

        # Add "Contact Info" and "Scan w/ Camera" text to the composite image
        side_font_size = qr_height_px // 12
        side_font = ImageFont.truetype("cour.ttf", side_font_size)

        contact_info_img = Image.new("RGB", side_font.getbbox("Contact Information")[2:], color="white")
        contact_info_draw = ImageDraw.Draw(contact_info_img)
        contact_info_draw.text((0, 0), "Contact Information", font=side_font, fill="black")
        contact_info_img = contact_info_img.rotate(90, expand=True)
        composite_img.paste(contact_info_img,
                            (qr_x - contact_info_img.width - 10, qr_y + (qr_height_px - contact_info_img.height) // 2))

        scan_img = Image.new("RGB", side_font.getbbox("Scan w/ Camera")[2:], color="white")
        scan_draw = ImageDraw.Draw(scan_img)
        scan_draw.text((0, 0), "Scan w/ Camera", font=side_font, fill="black")
        scan_img = scan_img.rotate(270, expand=True)
        composite_img.paste(scan_img, (qr_x + qr_width_px + 10, qr_y + (qr_height_px - scan_img.height) // 2))

        # Draw user's full name and border text
        draw = ImageDraw.Draw(composite_img)
        font_size = qr_height_px // 9
        font = ImageFont.truetype("arial.ttf", font_size)

        text_width, text_height = font.getbbox(full_name)[2:]
        text_x = (width_px - text_width) // 2
        text_y = (height_px // 4 - text_height) // 2
        draw.text((text_x, text_y), full_name, font=font, fill="black")

        border_text = ("12th PHILMACH ● " * 7).strip()  # Repeat the border text
        small_font_size = qr_height_px // 25
        small_font = ImageFont.truetype("arial.ttf", small_font_size)

        # Add border text to all sides
        draw.text((0, 0), border_text, font=small_font, fill="black")
        bottom_text_width, _ = small_font.getbbox(border_text)[2:]
        draw.text(((width_px - bottom_text_width) // 2, height_px - small_font_size), border_text, font=small_font,
                  fill="black")

        left_text_img = Image.new("RGB", small_font.getbbox(border_text)[2:], color="white")
        left_text_draw = ImageDraw.Draw(left_text_img)
        left_text_draw.text((0, 0), border_text, font=small_font, fill="black")
        left_text_img = left_text_img.rotate(90, expand=True)
        composite_img.paste(left_text_img, (0, (height_px - left_text_img.height) // 2))

        right_text_img = Image.new("RGB", small_font.getbbox(border_text)[2:], color="white")
        right_text_draw = ImageDraw.Draw(right_text_img)
        right_text_draw.text((0, 0), border_text, font=small_font, fill="black")
        right_text_img = right_text_img.rotate(270, expand=True)
        composite_img.paste(right_text_img, (width_px - right_text_img.width, (height_px - right_text_img.height) // 2))

        # Save the composite image
        composite_filename = qr_filename.replace(".png", "_composite.png")
        composite_img.save(composite_filename)
        # logging.info(f"Composite image saved as {composite_filename}")

        # Start the print job
        printer_name = win32print.GetDefaultPrinter()
        # logging.info(f"Printing to {printer_name}.")

        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc(composite_filename)
        hdc.StartPage()

        printer_width = hdc.GetDeviceCaps(8)
        printer_height = hdc.GetDeviceCaps(10)

        x_position = (printer_width - width_px) // 2
        y_position = (printer_height - height_px) // 2

        dib = ImageWin.Dib(composite_img)
        dib.draw(hdc.GetHandleOutput(), (x_position, y_position, x_position + width_px, y_position + height_px))

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

        logging.info(f"Print job completed for {composite_filename}.")
        clean_file(composite_filename)
    except Exception as e:
        logging.error(f"Error occurred while printing QR code: {e}")


def decode_qr_to_vcard():
    qr_string = input("Enter the QR hash: ")

    try:
        components = qr_string.split(";")
        if len(components) != 6:
            raise ValueError("Invalid QR data format.")

        user_hash = components[0]
        first_name, last_name, email, number, company = components[1:6]
        logging.info(f"Decoding QR code with hash: {user_hash}")

        user_info = f"{first_name};{last_name};{email};{number};{company}"

        if not verify_hash(user_info, user_hash):
            raise ValueError("Hash mismatch! QR code does not match the expected hash.")

        vcard_data = f"""
BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name};;;
EMAIL:{email}
TEL:{number}
ORG:{company}
END:VCARD
        """.strip()

        # logging.info(f"Generated vCard for {last_name}.")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=5,
            border=1,
        )
        qr.add_data(vcard_data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        os.makedirs("vcard_qr_codes", exist_ok=True)
        qr_filename = os.path.join("vcard_qr_codes", f"{first_name}_{last_name}_vcard_qr.png")
        img.save(qr_filename)
        # logging.info(f"vCard QR code saved as {qr_filename}")

        print_qr_code_with_details(qr_filename, first_name, last_name)
        clean_file(qr_filename)
    except ValueError as e:
        logging.error(f"Error: {e}")


def main_menu():
    while True:
        print("QR Code Processing System")
        print("1. Start QR Scanner and Printer")
        print("q. Quit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            scanning = True
            while scanning:
                try:
                    decode_qr_to_vcard()
                except KeyboardInterrupt:
                    print("Scanning stopped.")
                    logging.info("User interrupted the scanning process.")
                    scanning = False

        elif choice == "q":
            print("Exiting...")
            logging.info("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")
            logging.warning("Invalid menu choice.")


if __name__ == "__main__":
    main_menu()
