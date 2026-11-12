import json
import os
import time
import hashlib
from datetime import datetime

MAX_ATTEMPTS = 6
LOCK_AFTER_ATTEMPTS = 3
LOCK_SECONDS = 60

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_new_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    has_upper = False
    has_lower = False
    has_digit = False

    for ahh in password:
        if ahh.isupper():
            has_upper = True
        elif ahh.islower():
            has_lower = True
        elif ahh.isdigit():
            has_digit = True

    if not has_upper:
        return "Password must contain an uppercase letter."
    if not has_lower:
        return "Password must contain a lowercase letter."
    if not has_digit:
        return "Password must contain a digit."

    return ""

def wait_if_locked(user, data, save_data):
    until = user.get("lockout_until")

    if until is None:
        return

    now_ts = datetime.now().timestamp()
    if now_ts >= until:
        user["lockout_until"] = None
        save_data(data)
        return

    print("Too many failed login attempts.")

    while True:
        left = int(until - datetime.now().timestamp())
        if left <= 0:
            break
        
        mins, secs = divmod(left, 60)
        print(f"Please wait: {mins:02d}:{secs:02d}")
        time.sleep(1)

    print("Please wait: 00:00")
    print("You may try again.")

    user["lockout_until"] = None
    save_data(data)

def login(data, save_data):
    username = input("Username: ").strip()

    if username not in data:
        print("Invalid username or password.")
        return None

    user = data[username]

    if user.get("is_blocked", False):
        print("Maximum login attempts exceeded.")
        print("Your card has been blocked.")
        print("Please contact the bank administrator.")
        return None

    while True:
        wait_if_locked(user, data, save_data)

        password = input("Password: ")
        hashed_input = hash_password(password)

        if hashed_input == user["password_hash"]:
            user["failed_attempts"] = 0
            user["lockout_until"] = None
            save_data(data)
            print(f"Uğurlu giriş! Xoş gəldiniz, {username}.")
            return username

        user["failed_attempts"] = user.get("failed_attempts", 0) + 1
        attempts = user["failed_attempts"]
        print("Incorrect password. Attempt: " + str(attempts) + "/" + str(MAX_ATTEMPTS))

        if attempts >= MAX_ATTEMPTS:
            user["is_blocked"] = True
            user["lockout_until"] = None
            save_data(data)
            print("Maximum login attempts exceeded.")
            print("Your card has been blocked.")
            print("Please contact the bank administrator.")
            return None

        # 3-cü cəhddə təkrar çap olunmaması üçün birbaşa vaxtı təyin edirik
        if attempts == LOCK_AFTER_ATTEMPTS:
            user["lockout_until"] = datetime.now().timestamp() + LOCK_SECONDS
            save_data(data)
            continue

        save_data(data)

def change_password(data, username, save_data):
    user = data[username]

    current = input("Enter current password: ")
    if hash_password(current) != user["password_hash"]:
        print("Current password is incorrect.")
        return False

    new_password = input("Enter new password: ")

    message = check_new_password(new_password)
    if message != "":
        print(message)
        return False

    if hash_password(new_password) == user["password_hash"]:
        print("New password must be different from the old password.")
        return False

    confirm = input("Re-enter new password: ")
    if confirm != new_password:
        print("Passwords do not match.")
        return False

    user["password_hash"] = hash_password(new_password)
    save_data(data)
    print("Password changed successfully.")
    return True

if __name__ == "__main__":
    filename = "users.json"

    def save_data(d):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=4, ensure_ascii=False)

    if os.path.exists(filename):
        os.remove(filename)

    def create_user_dict(raw_password):
        return {
            "password_hash": hash_password(raw_password),
            "failed_attempts": 0,
            "lockout_until": None,
            "is_blocked": False,
            "balance": 2500.00,
            "transaction_history": []
        }

    initial_data = {
        "user01": create_user_dict("Test@123"),
        "user02": create_user_dict("Test@456"),
        "user03": create_user_dict("Test@789")
    }
    save_data(initial_data)

    with open(filename, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    logged_user = login(test_data, save_data)

    if logged_user is not None:
        answer = input("Change password? (Y/N): ").strip().upper()
        if answer == "Y":
            change_password(test_data, logged_user, save_data)
    else:
        print("Login failed.")