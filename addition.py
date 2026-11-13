from storage import save_data, today_str       #* today_str used for getting the current date, will be used in transfer validation and daily limit checks.
from datetime import datetime       #* Used for getting the exact time of transactions, will be used in transaction history records.
import math

def execute_transfer(data, sender, recipient_account, amount):
    """Move money between two accounts. Call only after validation passed."""

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sender_data = data["users"][sender]
    recipient_data = None
    for user_data in data["users"].values():
        if user_data["account_number"] == recipient_account:
            recipient_data = user_data
            break

    sender_balance_before = sender_data["balance"]

    recipient_balance_before = recipient_data["balance"]

    sender_data["balance"] = round(sender_data["balance"] - amount, 2)
    recipient_data["balance"] = round(recipient_data["balance"] + amount, 2)

    if sender_data["daily_transfer_date"] != today_str():
        sender_data["daily_transfers"] = 0
        sender_data["daily_transfer_date"] = today_str()
    sender_data["daily_transfers"] += 1

    txn_id = f"TXN{data['next_txn_id']:04d}"
    data["next_txn_id"] += 1

    sender_txn_record = {
        "id": txn_id,
        "date": now_str,
        "type": "Transfer sent",
        "amount": -amount,
        "counterparty": recipient_account,
        "balance_before": sender_balance_before,
        "balance_after": sender_data["balance"],
        "fee": 0.00
    }

    recipient_txn_record = {
        "id": txn_id,
        "date": now_str,
        "type": "Transfer received",
        "amount": amount,
        "counterparty": sender_data["account_number"],
        "balance_before": recipient_balance_before,
        "balance_after": recipient_data["balance"],
        "fee": 0.00
    }

    sender_data["history"].append(sender_txn_record)
    recipient_data["history"].append(recipient_txn_record)

    save_data(data)

def validate_transfer(data, sender):
    """Returns None if valid, otherwise returns an error message string."""
    
    if sender not in data["users"]:
            return "Sender does not exist."
    
    DAILY_TRANSFER_LIMIT = 5

    if get_today_transfer_count(data["users"][sender]) >= DAILY_TRANSFER_LIMIT:
      return "Sender has reached the daily transfer limit."

    print(f"Daily transfer limit: {DAILY_TRANSFER_LIMIT} transfers")
    print("You have made {} transfers today.".format(get_today_transfer_count(data["users"][sender])))
    print("Your balance: {:.2f} AZN".format(data["users"][sender]["balance"]))

    recipient_account = input("Enter recipient account number: ")
    
    if recipient_account not in [user["account_number"] for user in data["users"].values()]:
        return "Recipient account does not exist."
            
    if data["users"][sender]["account_number"] == recipient_account:
        return "Sender and recipient can't be the same."
    
    try:
        amount = float(input("Enter transfer amount: "))
        if not math.isfinite(amount):
            raise ValueError
    except ValueError:
        return "Amount must be a number."
    
    if round(amount, 2) != amount:
        return "Amount can have at most two decimal places."

    if amount <= 0:
        return "Transfer amount must be greater than zero."
    
    if amount > data["users"][sender]["balance"]:
        return "Insufficient funds for the transfer."
    
    confirmation = input(f"Confirm transfer of {amount:.2f} AZN to account {recipient_account}? (Y/N): ")
    
    if confirmation.lower() == "n":
        return "Transfer cancelled by user."
    elif confirmation.lower() == "y":
        return None         # Valid transfer
    else:
        return "Invalid input. Transfer cancelled."

def get_today_transfer_count(sender_data):
    if sender_data["daily_transfer_date"] != today_str():
        return 0          # Stored count is from an earlier day
    return sender_data["daily_transfers"]