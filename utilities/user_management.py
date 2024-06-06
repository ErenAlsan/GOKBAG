import os
import random
import string
import hashlib
import json

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def generate_salt(length=16):
    return os.urandom(length)

def hash_password(password, salt):
    return hashlib.sha256(salt + password.encode()).hexdigest()

def update_user_data(users, user_data_file):
    with open(user_data_file, 'w') as f:
        json.dump(users, f)

def load_users(user_data_file):
    if not os.path.exists(user_data_file):
        users = {
            'user1': {'password': hash_password('user1pass', (salt := generate_salt())), 'salt': salt.hex()},
            'user2': {'password': hash_password('user2pass', (salt := generate_salt())), 'salt': salt.hex()},
            'user3': {'password': hash_password('user3pass', (salt := generate_salt())), 'salt': salt.hex()},
            'user4': {'password': hash_password('user4pass', (salt := generate_salt())), 'salt': salt.hex()},
            'user5': {'password': hash_password('user5pass', (salt := generate_salt())), 'salt': salt.hex()},
            'admin': {'password': hash_password('adminpass', (salt := generate_salt())), 'salt': salt.hex()}
        }
        update_user_data(users, user_data_file)
    else:
        with open(user_data_file, 'r') as f:
            users = json.load(f)

        for username, user_data in users.items():
            if isinstance(user_data, str):
                salt = generate_salt()
                hashed_password = hash_password(user_data, salt)
                users[username] = {'password': hashed_password, 'salt': salt.hex()}
                update_user_data(users, user_data_file)

    return users
