# Helper function to generate a consistent hash based on user info
import base64
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Retrieve the predefined salt from the .env file
HASH_SALT = os.getenv('HASH_SALT')


def generate_hash(user_info):
    # Encode the user info to Base64
    encoded_info = base64.b32encode(user_info.encode()).decode()
    return encoded_info


def decode_hash(user_hash):
    # Decode the Base32 encoded user info
    decoded_info = base64.b32decode(user_hash).decode()

    # Split the decoded info by ';' to return the individual components
    split_info = decoded_info.split(';')
    return split_info


def clean_file(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
            logging.info(f"QR code file {filename} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete QR code file {filename}: {e}")