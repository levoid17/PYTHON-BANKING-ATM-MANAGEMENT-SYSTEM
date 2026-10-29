import json
import os 

DATA_PATH = "data/bank_data.json"

def _default_data():
    return {
        "atm_cash": 5000.00,
        "users": {
            "user01": {
                "account_number": "10010001", 
                "password": "Test@123", 
                "balance": 2500.00, 
                "status": "active", 
                "history": [],
                "blocked": False,
                "failed_attempts": 0,
                "lockout_until": None,
                "today_deposits": 0.00,
                "today_withdrawals": 0.00
            },
            "user02": {
                "account_number": "10010002", 
                "password": "Test@456", 
                "balance": 1500.00, 
                "status": "active", 
                "history": [],
                "blocked": False,
                "failed_attempts": 0,
                "lockout_until": None,
                "today_deposits": 0.00,
                "today_withdrawals": 0.00
            },
            "user03": {
                "account_number": "10010003", 
                "password": "Test@789", 
                "balance": 3000.00, 
                "status": "active", 
                "history": [],
                "blocked": False,
                "failed_attempts": 0,
                "lockout_until": None,
                "today_deposits": 0.00,
                "today_withdrawals": 0.00
            },
        },
    }

def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        data = _default_data()
        save_data(data, path)
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Data file is damaged. Starting with default data")
        return _default_data()

def save_data(data, path=DATA_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception as e:
        print(f"Error saving data: {e}")