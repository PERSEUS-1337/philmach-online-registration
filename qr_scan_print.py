import os

import win32print, win32ui
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageWin


def print_qr_code_with_details(qr_filename, first_name, last_name):
    full_name = f"{first_name} {last_name}"

    # Define the desired size in pixels
    width_px = 525
    height_px = 365

    # Create a new blank image for the composite
    composite_img = Image.new("RGB", (width_px, height_px), color="white")

    # Load the QR code image
    qr_img = Image.open(qr_filename)
    qr_img = qr_img.convert("RGB")  # Ensure the image is in RGB mode

    # Define the QR code size to be 3/4 of the total height
    qr_height_px = int(height_px * 3 / 4)
    qr_width_px = qr_height_px  # Keep the QR code square

    # Resize the QR code image
    qr_img = qr_img.resize((qr_width_px, qr_height_px), Image.LANCZOS)

    # Calculate the position to center the QR code at the bottom
    bottom_margin = 15
    qr_x = (width_px - qr_width_px) // 2
    qr_y = height_px - qr_height_px - bottom_margin

    # Paste the QR code image into the composite
    composite_img.paste(qr_img, (qr_x, qr_y))

    # Rotate and add "Contact Info" on the left side of the QR code
    padding = 10
    contact_info_text = "Contact Information"
    side_font_size = qr_height_px // 12  # Adjust font size for side text
    side_font = ImageFont.truetype("cour.ttf", side_font_size)
    contact_info_img = Image.new("RGB", side_font.getbbox(contact_info_text)[2:], color="white")
    contact_info_draw = ImageDraw.Draw(contact_info_img)
    contact_info_draw.text((0, 0), contact_info_text, font=side_font, fill="black")
    contact_info_img = contact_info_img.rotate(90, expand=True)
    composite_img.paste(contact_info_img,
                        (qr_x - contact_info_img.width - padding, qr_y + (qr_height_px - contact_info_img.height) // 2))

    # Rotate and add "Scan w/ Camera" on the right side of the QR code
    scan_text = "Scan w/ Camera"
    scan_img = Image.new("RGB", side_font.getbbox(scan_text)[2:], color="white")
    scan_draw = ImageDraw.Draw(scan_img)
    scan_draw.text((0, 0), scan_text, font=side_font, fill="black")
    scan_img = scan_img.rotate(270, expand=True)
    composite_img.paste(scan_img, (qr_x + qr_width_px + padding, qr_y + (qr_height_px - scan_img.height) // 2))

    # Draw the user's full name at the top
    draw = ImageDraw.Draw(composite_img)

    # Define font size for the full name
    font_size = qr_height_px // 9  # Make the font size proportional to the QR code height
    font = ImageFont.truetype("arial.ttf", font_size)

    # Calculate the position for the full name (centered at the top)
    text_width, text_height = font.getbbox(full_name)[2:]
    text_x = (width_px - text_width) // 2
    text_y = (height_px // 4 - text_height) // 2  # Centered in the top 1/4 height

    # Add the full name to the image
    draw.text((text_x, text_y), full_name, font=font, fill="black")

    # Add "PHILMACH 2024 PHILMACH 2024" around the border
    border_text = ("12th PHILMACH ● 12th PHILMACH ● 12th PHILMACH ● 12th PHILMACH ● 12th PHILMACH ● 12th PHILMACH ● "
                   "12th PHILMACH ●")
    small_font_size = qr_height_px // 25  # Very small font size for the border text
    small_font = ImageFont.truetype("arial.ttf", small_font_size)

    # Top border
    draw.text((0, 0), border_text, font=small_font, fill="black")

    # Bottom border
    bottom_text_width, _ = small_font.getbbox(border_text)[2:]
    draw.text(((width_px - bottom_text_width) // 2, height_px - small_font_size), border_text, font=small_font,
              fill="black")

    # Left border (rotated 90 degrees)
    left_text_img = Image.new("RGB", small_font.getbbox(border_text)[2:], color="white")
    left_text_draw = ImageDraw.Draw(left_text_img)
    left_text_draw.text((0, 0), border_text, font=small_font, fill="black")
    left_text_img = left_text_img.rotate(90, expand=True)
    composite_img.paste(left_text_img, (0, (height_px - left_text_img.height) // 2))

    # Right border (rotated 270 degrees)
    right_text_img = Image.new("RGB", small_font.getbbox(border_text)[2:], color="white")
    right_text_draw = ImageDraw.Draw(right_text_img)
    right_text_draw.text((0, 0), border_text, font=small_font, fill="black")
    right_text_img = right_text_img.rotate(270, expand=True)
    composite_img.paste(right_text_img, (width_px - right_text_img.width, (height_px - right_text_img.height) // 2))

    # Add a thin border around the entire image
    # border_thickness = 2  # Set the border thickness (in pixels)
    # draw.rectangle(
    #     [border_thickness // 2, border_thickness // 2, width_px - border_thickness // 2, height_px - border_thickness // 2],
    #     outline="green",
    #     width=border_thickness
    # )

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
            box_size=5,
            border=1,
            mask_pattern=3
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

        print_qr_code_with_details(qr_filename, first_name, last_name)
        # return qr_filename

    except ValueError:
        print("Error: Invalid QR data format.")
        return None


# Main menu to choose between camera or keyboard input
def main_menu():
    while True:
        print("QR Code Processing System")
        print("1. Start QR Scanner and Printer)")
        print("q. Quit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            decode_qr_to_vcard()
        elif choice == "q":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


# Start the main menu
if __name__ == "__main__":
    main_menu()
