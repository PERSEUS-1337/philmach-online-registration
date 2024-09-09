# Helper function to generate a consistent hash based on user info
import hashlib
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
    # Combine the user info with the predefined salt
    combined = user_info + HASH_SALT
    return hashlib.sha256(combined.encode()).hexdigest()[:32]  # Shortened hash for brevity


def verify_hash(user_info, expected_hash):
    combined = user_info + HASH_SALT
    generated_hash = hashlib.sha256(combined.encode()).hexdigest()[:32]
    print(f"Generated Hash: {generated_hash}")
    print(f"Expected Hash: {expected_hash}")
    return generated_hash == expected_hash


def clean_file(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
            logging.info(f"QR code file {filename} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete QR code file {filename}: {e}")