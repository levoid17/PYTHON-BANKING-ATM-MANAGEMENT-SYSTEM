import json
import os
import hashlib
from datetime import date

DATA_PATH = "data/bank_data.json"


def today_str():
    return date.today().isoformat()


def _password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _default_data():            # If data is not found in database, it uses default demo accounts
    return {
        "atm_cash": 5000.00,
        "next_txn_id": 1,
        "users": {
            "user01": {"account_number": "10010001", "password_hash": _password_hash("Test@123"), "balance": 2500.00, "status": "active", "history": [], "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 1},
            "user02": {"account_number": "10010002", "password_hash": _password_hash("Test@456"), "balance": 1500.00, "status": "active", "history": [], "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 1},
            "user03": {"account_number": "10010003", "password_hash": _password_hash("Test@789"), "balance": 3000.00, "status": "active", "history": [], "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 1},
        },
    }

def load_data(path=DATA_PATH):          # It is for loading last changes after starting program
    if not os.path.exists(path):
        data = _default_data()
        save_data(data)
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("next_txn_id", 1)
            return data
    except json.JSONDecodeError:
        print("Error: Data file is damaged. Starting with default data")
        return _default_data()

def save_data(data, path = DATA_PATH):       # This function is for saving the changes in database for next start of program.
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp_path, path)
