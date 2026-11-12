import json
import os 

DATA_PATH = "data/bank_data.json"

def _default_data():            # If data is not found in database, it uses default demo accounts
    return {
        "atm_cash": 5000.00,
        "history": [],
        "users": {
            "user01": {"account_number": "10010001", "password": "Test@123", "balance": 2500.00, "status": "active", "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 1},
            "user02": {"account_number": "10010002", "password": "Test@456", "balance": 1500.00, "status": "active", "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 2},
            "user03": {"account_number": "10010003", "password": "Test@789", "balance": 3000.00, "status": "active", "daily_transfers": 0, "daily_transfer_date": None, "last_login": None, "last_transaction_time": None, "next_txn_id": 3},
        },
    }

def load_data(path=DATA_PATH):          # It is for loading last changes after starting program
    if not os.path.exists(path):
        data = _default_data()
        save_data(data)
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Data file is damaged. Starting with default data")
        return _default_data()

def save_data(data, path = DATA_PATH):       # This function is for saving the changes in database for next start of program.
    os.makedirs("data", exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp_path, path)

