from datetime import date, datetime

DAILY_DEPOSIT_LIMIT = 2000.00
DAILY_WITHDRAWAL_LIMIT = 1000.00
FEE_FREE_WITHDRAWAL_ALLOWANCE = 500.00
WITHDRAWAL_FEE_RATE = 0.02
MAX_DAILY_TRANSFERS = 5
HISTORY_LIMIT = 20


def _read_amount(prompt):
    amount_text = input(prompt).strip()
    try:
        amount = float(amount_text)
    except ValueError:
        print("Transaction declined: please enter a valid number.")
        return None

    if amount <= 0:
        print("Transaction declined: amount must be greater than zero.")
        return None

    if "." in amount_text and len(amount_text.split(".", 1)[1]) > 2:
        print("Transaction declined: maximum two decimal places are allowed.")
        return None

    return amount


def display_account_info(username, account_number, balance, status="Active"):
    print("\nACCOUNT INFORMATION")
    print(f"Account Holder: {username}")
    print(f"Account Number: {account_number}")
    print(f"Available Balance: {balance:.2f} AZN")
    print(f"Account Status: {status}")


def display_daily_limits(today_deposits, today_withdrawals, outgoing_transfers=0):
    deposit_remaining = max(0.0, DAILY_DEPOSIT_LIMIT - today_deposits)
    withdrawal_remaining = max(0.0, DAILY_WITHDRAWAL_LIMIT - today_withdrawals)
    fee_free_remaining = max(0.0, FEE_FREE_WITHDRAWAL_ALLOWANCE - today_withdrawals)

    print("\nDAILY LIMITS")
    print(f"Deposit used: {today_deposits:.2f}/{DAILY_DEPOSIT_LIMIT:.2f} AZN")
    print(f"Deposit remaining: {deposit_remaining:.2f} AZN")
    print(f"Cash withdrawn: {today_withdrawals:.2f}/{DAILY_WITHDRAWAL_LIMIT:.2f} AZN")
    print(f"Cash withdrawal remaining: {withdrawal_remaining:.2f} AZN")
    print(f"Fee-free cash remaining: {fee_free_remaining:.2f} AZN")
    print(f"Outgoing transfers: {outgoing_transfers}/5")


def deposit_money(username, current_balance, today_deposits, atm_cash):
    print(f"\nDeposited today: {today_deposits:.2f} AZN")
    print(f"Daily deposit maximum: {DAILY_DEPOSIT_LIMIT:.2f} AZN")
    print(f"Remaining deposit allowance: {max(0.0, DAILY_DEPOSIT_LIMIT - today_deposits):.2f} AZN")

    amount = _read_amount("Requested deposit amount: ")
    if amount is None:
        return current_balance, today_deposits, atm_cash

    if today_deposits + amount > DAILY_DEPOSIT_LIMIT:
        print("Deposit declined: daily deposit limit would be exceeded.")
        return current_balance, today_deposits, atm_cash

    current_balance += amount
    today_deposits += amount
    atm_cash += amount

    print(f"Deposit successful: {amount:.2f} AZN")
    print(f"New account balance: {current_balance:.2f} AZN")
    return current_balance, today_deposits, atm_cash


def withdraw_money(username, current_balance, today_withdrawals, atm_cash):
    print(f"\nCash withdrawn today: {today_withdrawals:.2f} AZN")
    print(f"Daily withdrawal maximum: {DAILY_WITHDRAWAL_LIMIT:.2f} AZN")
    print(f"Remaining withdrawal allowance: {max(0.0, DAILY_WITHDRAWAL_LIMIT - today_withdrawals):.2f} AZN")

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
    charged_at_fee_rate = max(0.0, amount - fee_free_remaining)
    commission = round(charged_at_fee_rate * WITHDRAWAL_FEE_RATE, 2)
    total_deduction = amount + commission

    if current_balance < total_deduction:
        print("Withdrawal declined: insufficient balance to cover cash and commission.")
        return current_balance, today_withdrawals, atm_cash

    current_balance -= total_deduction
    today_withdrawals += amount
    atm_cash -= amount

    if commission > 0:
        print(f"Withdrawal commission: {commission:.2f} AZN")

    print(f"Cash paid out: {amount:.2f} AZN")
    print(f"Amount deducted from account: {total_deduction:.2f} AZN")
    print(f"New account balance: {current_balance:.2f} AZN")
    return current_balance, today_withdrawals, atm_cash


def add_transaction_entry(user, kind, amount, details):
    history = user.setdefault("history", [])
    next_txn_id = user.get("next_txn_id", 1)
    history.append(
        {
            "id": next_txn_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": kind,
            "amount": round(amount, 2),
            "details": details,
        }
    )
    if len(history) > HISTORY_LIMIT:
        del history[:-HISTORY_LIMIT]
    user["next_txn_id"] = next_txn_id + 1
    user["last_transaction_time"] = datetime.now().isoformat()


def check_balance(current_balance):
    print(f"\nCurrent balance: {current_balance:.2f} AZN")


def transfer_money(data, sender_username):
    sender = data["users"][sender_username]
    today = date.today().isoformat()
    if sender.get("daily_transfer_date") != today:
        sender["daily_transfer_date"] = today
        sender["daily_transfers"] = 0

    if sender.get("daily_transfers", 0) >= MAX_DAILY_TRANSFERS:
        print("Transfer declined: daily transfer count limit reached.")
        return False

    recipient_account = input("Recipient account number: ").strip()
    recipient_username = None
    for username, user in data["users"].items():
        if user.get("account_number") == recipient_account:
            recipient_username = username
            break

    if recipient_username is None:
        print("Transfer declined: recipient account not found.")
        return False

    if recipient_username == sender_username:
        print("Transfer declined: you cannot transfer to your own account.")
        return False

    recipient = data["users"][recipient_username]
    amount = _read_amount("Transfer amount: ")
    if amount is None:
        return False

    if sender["balance"] < amount:
        print("Transfer declined: insufficient balance.")
        return False

    sender["balance"] -= amount
    recipient["balance"] += amount
    sender["daily_transfers"] = sender.get("daily_transfers", 0) + 1
    sender["daily_transfer_date"] = today

    add_transaction_entry(
        sender,
        "transfer_out",
        amount,
        f"to {recipient.get('account_number')}",
    )
    add_transaction_entry(
        recipient,
        "transfer_in",
        amount,
        f"from {sender.get('account_number')}",
    )

    print(f"Transfer successful: {amount:.2f} AZN sent to {recipient.get('account_number')}.")
    print(f"New account balance: {sender['balance']:.2f} AZN")
    return True


def show_transaction_history(user):
    history = user.get("history", [])
    if not history:
        print("\nNo transactions yet.")
        return

    print("\nTRANSACTION HISTORY")
    for item in reversed(history[-10:]):
        print(
            f"[{item.get('id')}] {item.get('time')} | {item.get('type')} | "
            f"{item.get('amount', 0.0):.2f} AZN | {item.get('details', '')}"
        )
