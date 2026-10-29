import time

MAX_ATTEMPTS = 6
LOCK_AFTER_ATTEMPTS = 3
LOCK_SECONDS = 60


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
    until = user["lockout_until"]

    if until is None:
        return

    if time.time() >= until:
        user["lockout_until"] = None
        save_data(data)
        return

    print("Too many failed login attempts.")

    while time.time() < until:
        left = int(until - time.time())
        # \033[K clears the line so no old characters stick around
        print(f"\rPlease wait: 00:{left:02d}\033[K", end="", flush=True)
        time.sleep(1)

    # Clear the countdown line completely and print the final message cleanly
    print("\rYou may try again.\033[K")

    user["lockout_until"] = None
    save_data(data)


def login(data, save_data):
    username = input("Username: ").strip()

    if username not in data["users"]:
        print("Invalid username or password.")
        return None

    user = data["users"][username]

    if user["blocked"]:
        print("Your card has been blocked.")
        print("Please contact the bank administrator.")
        return None

    while True:
        wait_if_locked(user, data, save_data)

        password = input("Password: ")

        if password == user["password"]:
            user["failed_attempts"] = 0
            user["lockout_until"] = None
            save_data(data)
            return username

        user["failed_attempts"] = user["failed_attempts"] + 1
        attempts = user["failed_attempts"]
        print("Incorrect password. Attempt: " + str(attempts) + "/" + str(MAX_ATTEMPTS))

        if attempts >= MAX_ATTEMPTS:
            user["blocked"] = True
            user["lockout_until"] = None
            save_data(data)
            print("Maximum login attempts exceeded.")
            print("Your card has been blocked.")
            print("Please contact the bank administrator.")
            return None

        if attempts == LOCK_AFTER_ATTEMPTS:
            user["lockout_until"] = time.time() + LOCK_SECONDS

        save_data(data)


def change_password(data, username, save_data):
    user = data["users"][username]

    current = input("Enter current password: ")
    if current != user["password"]:
        print("Current password is incorrect.")
        return False

    new_password = input("Enter new password: ")

    message = check_new_password(new_password)
    if message != "":
        print(message)
        return False

    if new_password == user["password"]:
        print("New password must be different from the old password.")
        return False

    confirm = input("Re-enter new password: ")
    if confirm != new_password:
        print("Passwords do not match.")
        return False

    user["password"] = new_password
    save_data(data)
    print("Password changed successfully.")
    return True


if __name__ == "__main__":
    def save_data(data):
        pass

    test_data = {
        "users": {
            "user01": {"password": "Test@123", "blocked": False,
                       "failed_attempts": 0, "lockout_until": None},
            "user02": {"password": "Test@456", "blocked": False,
                       "failed_attempts": 0, "lockout_until": None},
            "user03": {"password": "Test@789", "blocked": False,
                       "failed_attempts": 0, "lockout_until": None},
        }
    }

    logged_user = login(test_data, save_data)

    if logged_user is not None:
        print("Welcome, " + logged_user + "!")
        answer = input("Change password? (Y/N): ").strip().upper()
        if answer == "Y":
            change_password(test_data, logged_user, save_data)
    else:
        print("Login failed.")