import csv
import os
from datetime import datetime
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Create 'flight_logs' directory if it doesn't exist
log_folder = "flight_logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_path = os.path.join(log_folder, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")

# Encryption key (must be 32 bytes long for AES-256)
encryption_key = b'Sixteen byte key'

def make_csv(coords, filename=log_file_path):
    # Writing to CSV
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)

        # Write each tuple as a row in the CSV file
        csv_writer.writerows(coords)

    print(f'CSV file "{filename}" created successfully.')

    # Encrypt the file
    encrypt_file(filename)


def encrypt_file(filename):
    # Read the file content
    with open(filename, 'rb') as f:
        data = f.read()

    # Generate a random initialization vector
    iv = os.urandom(16)

    # Create a cipher using AES encryption in CBC mode
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data and add padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()

    # Write the encrypted data along with the IV to the file
    with open(filename, 'wb') as f:
        f.write(iv + cipher_text)

    print(f'File "{filename}" encrypted successfully.')


def decrypt_file(filename):
    # Read the encrypted file content
    with open(filename, 'rb') as f:
        encrypted_data = f.read()

    # Extract the IV from the file
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    # Create a cipher using AES encryption in CBC mode
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data and remove padding
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data


def csv_to_list(filename):
    # Decrypt the file
    decrypted_data = decrypt_file(filename)

    # Decode and parse the decrypted CSV content
    coords = []
    decoded_data = decrypted_data.decode('utf-8')
    csv_reader = csv.reader(decoded_data.splitlines())
    for row in csv_reader:
        coords.append((float(row[0]), float(row[1]), float(row[2])))

    return coords
