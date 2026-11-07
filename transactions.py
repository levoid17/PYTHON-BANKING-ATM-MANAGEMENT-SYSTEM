from datetime import date, datetime
import math


DAILY_DEPOSIT_LIMIT = 2000.00
DAILY_WITHDRAWAL_LIMIT = 1000.00
DAILY_TRANSFER_LIMIT = 5
FEE_FREE_WITHDRAWAL_ALLOWANCE = 500.00
WITHDRAWAL_FEE_RATE = 0.02


def _read_amount(prompt):
    amount_text = input(prompt).strip()
    try:
        amount = float(amount_text)
    except ValueError:
        print("Transaction declined: please enter a valid number.")
        return None

    if not math.isfinite(amount) or amount <= 0:
        print("Transaction declined: amount must be greater than zero.")
        return None

    decimal_part = amount_text.split(".", 1)[1] if "." in amount_text else ""
    if len(decimal_part) > 2:
        print("Transaction declined: maximum two decimal places are allowed.")
        return None

    return round(amount, 2)


def _record_transaction(user, transaction_type, amount, description, balance):
    history = user.setdefault("history", [])
    transaction_id = user.get("next_txn_id", 1)
    history.append(
        {
            "id": transaction_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "amount": round(amount, 2),
            "description": description,
            "balance": round(balance, 2),
        }
    )
    user["next_txn_id"] = transaction_id + 1
    user["last_transaction_time"] = datetime.now().isoformat(timespec="seconds")


def display_account_info(username, account_number, balance, status="active"):
    print("\nACCOUNT INFORMATION")
    print(f"Account Holder: {username}")
    print(f"Account Number: {account_number}")
    print(f"Available Balance: {balance:.2f} AZN")
    print(f"Account Status: {status}")


def display_balance(balance):
    print(f"\nAVAILABLE BALANCE: {balance:.2f} AZN")


def display_daily_limits(today_deposits, today_withdrawals, outgoing_transfers=0):
    deposit_remaining = max(0.0, DAILY_DEPOSIT_LIMIT - today_deposits)
    withdrawal_remaining = max(0.0, DAILY_WITHDRAWAL_LIMIT - today_withdrawals)
    fee_free_remaining = max(0.0, FEE_FREE_WITHDRAWAL_ALLOWANCE - today_withdrawals)
    transfer_remaining = max(0, DAILY_TRANSFER_LIMIT - outgoing_transfers)

    print("\nDAILY LIMITS")
    print(f"Deposit used: {today_deposits:.2f}/{DAILY_DEPOSIT_LIMIT:.2f} AZN")
    print(f"Deposit remaining: {deposit_remaining:.2f} AZN")
    print(f"Cash withdrawn: {today_withdrawals:.2f}/{DAILY_WITHDRAWAL_LIMIT:.2f} AZN")
    print(f"Cash withdrawal remaining: {withdrawal_remaining:.2f} AZN")
    print(f"Fee-free cash remaining: {fee_free_remaining:.2f} AZN")
    print(f"Outgoing transfers: {outgoing_transfers}/{DAILY_TRANSFER_LIMIT}")
    print(f"Transfers remaining: {transfer_remaining}")


def deposit_money(username, current_balance, today_deposits, atm_cash, user=None):
    print(f"\nDeposited today: {today_deposits:.2f} AZN")
    print(f"Daily deposit maximum: {DAILY_DEPOSIT_LIMIT:.2f} AZN")
    print(
        "Remaining deposit allowance: "
        f"{max(0.0, DAILY_DEPOSIT_LIMIT - today_deposits):.2f} AZN"
    )

    amount = _read_amount("Requested deposit amount: ")
    if amount is None:
        return current_balance, today_deposits, atm_cash

    if today_deposits + amount > DAILY_DEPOSIT_LIMIT:
        print("Deposit declined: daily deposit limit would be exceeded.")
        return current_balance, today_deposits, atm_cash

    current_balance = round(current_balance + amount, 2)
    today_deposits = round(today_deposits + amount, 2)
    atm_cash = round(atm_cash + amount, 2)
    if user is not None:
        _record_transaction(user, "DEPOSIT", amount, "Cash deposit", current_balance)

    print(f"Deposit successful: {amount:.2f} AZN")
    print(f"New account balance: {current_balance:.2f} AZN")
    return current_balance, today_deposits, atm_cash


def withdraw_money(username, current_balance, today_withdrawals, atm_cash, user=None):
    print(f"\nCash withdrawn today: {today_withdrawals:.2f} AZN")
    print(f"Daily withdrawal maximum: {DAILY_WITHDRAWAL_LIMIT:.2f} AZN")
    print(
        "Remaining withdrawal allowance: "
        f"{max(0.0, DAILY_WITHDRAWAL_LIMIT - today_withdrawals):.2f} AZN"
    )

    amount = _read_amount("Requested withdrawal amount: ")
    if amount is None:
        return current_balance, today_withdrawals, atm_cash

    if today_withdrawals + amount > DAILY_WITHDRAWAL_LIMIT:
        print("Withdrawal declined: daily withdrawal limit would be exceeded.")
        return current_balance, today_withdrawals, atm_cash
    if atm_cash < amount:
        print("Withdrawal declined: ATM does not have enough cash.")
        return current_balance, today_withdrawals, atm_cash

    fee_free_remaining = max(0.0, FEE_FREE_WITHDRAWAL_ALLOWANCE - today_withdrawals)
    commission = round(max(0.0, amount - fee_free_remaining) * WITHDRAWAL_FEE_RATE, 2)
    total_deduction = round(amount + commission, 2)
    if current_balance < total_deduction:
        print("Withdrawal declined: insufficient balance to cover cash and commission.")
        return current_balance, today_withdrawals, atm_cash

    current_balance = round(current_balance - total_deduction, 2)
    today_withdrawals = round(today_withdrawals + amount, 2)
    atm_cash = round(atm_cash - amount, 2)
    if user is not None:
        description = "Cash withdrawal"
        if commission:
            description += f" (commission {commission:.2f} AZN)"
        _record_transaction(user, "WITHDRAWAL", amount, description, current_balance)

    if commission > 0:
        print(f"Withdrawal commission: {commission:.2f} AZN")
    print(f"Cash paid out: {amount:.2f} AZN")
    print(f"Amount deducted from account: {total_deduction:.2f} AZN")
    print(f"New account balance: {current_balance:.2f} AZN")
    return current_balance, today_withdrawals, atm_cash


def transfer_money(data, username):
    sender = data["users"][username]
    recipient_key = input("Recipient username or account number: ").strip()
    recipient_name = next(
        (
            name
            for name, candidate in data["users"].items()
            if name == recipient_key or candidate.get("account_number") == recipient_key
        ),
        None,
    )
    if recipient_name is None:
        print("Transfer declined: recipient was not found.")
        return False
    if recipient_name == username:
        print("Transfer declined: you cannot transfer money to yourself.")
        return False

    transfer_count = sender.get("daily_transfers", 0)
    if transfer_count >= DAILY_TRANSFER_LIMIT:
        print("Transfer declined: daily transfer limit would be exceeded.")
        return False

    amount = _read_amount("Transfer amount: ")
    if amount is None:
        return False
    if sender["balance"] < amount:
        print("Transfer declined: insufficient balance.")
        return False

    recipient = data["users"][recipient_name]
    sender["balance"] = round(sender["balance"] - amount, 2)
    recipient["balance"] = round(recipient["balance"] + amount, 2)
    sender["daily_transfers"] = transfer_count + 1
    _record_transaction(
        sender,
        "TRANSFER OUT",
        amount,
        f"Transfer to {recipient_name}",
        sender["balance"],
    )
    _record_transaction(
        recipient,
        "TRANSFER IN",
        amount,
        f"Transfer from {username}",
        recipient["balance"],
    )
    print(
        f"Transfer successful: {amount:.2f} AZN sent to "
        f"{recipient_name}. New balance: {sender['balance']:.2f} AZN"
    )
    return True


def display_transaction_history(user):
    history = user.get("history", [])
    print("\nTRANSACTION HISTORY")
    if not history:
        print("No transactions found.")
        return

    for transaction in reversed(history):
        print(
            f"{transaction.get('date', 'Unknown date')} | "
            f"{transaction.get('type', 'TRANSACTION')} | "
            f"{transaction.get('amount', 0.0):.2f} AZN | "
            f"{transaction.get('description', '')} | "
            f"Balance: {transaction.get('balance', 0.0):.2f} AZN"
        )


def reset_daily_counters(user):
    today = date.today().isoformat()
    if user.get("daily_reset_date") != today:
        user["today_deposits"] = 0.0
        user["today_withdrawals"] = 0.0
        user["daily_transfers"] = 0
        user["daily_reset_date"] = today
