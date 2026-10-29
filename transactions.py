
def display_account_info(username, account_number, balance, status="Active"):
    """05. Account information and balance[cite: 5]"""
    print(f"\nAccount Holder\n{username}")
    print(f"Account Number: {account_number}")
    print(f"Available Balance: {balance:.2f} AZN")
    print(f"Account Status: {status}")


def display_daily_limits(today_deposits, today_withdrawals, outgoing_transfers=0):
    """11. Daily limits screen[cite: 11]"""
    DAILY_DEPOSIT_LIMIT = 2000.00
    DAILY_WITHDRAWAL_LIMIT = 1000.00
    FREE_ALLOWANCE = 500.00
    
    dep_remaining = DAILY_DEPOSIT_LIMIT - today_deposits
    with_remaining = DAILY_WITHDRAWAL_LIMIT - today_withdrawals
    
    if today_withdrawals <= FREE_ALLOWANCE:
        free_remaining = FREE_ALLOWANCE - today_withdrawals
    else:
        free_remaining = 0.00

    print("\nDAILY LIMITS")
    print(f"Deposit used:           {today_deposits:.2f}/{DAILY_DEPOSIT_LIMIT:.2f} AZN")
    print(f"Deposit remaining:      {dep_remaining:.2f} AZN")
    print(f"Cash withdrawn:         {today_withdrawals:.2f}/{DAILY_WITHDRAWAL_LIMIT:.2f} AZN")
    print(f"Cash withdrawal remaining: {with_remaining:.2f} AZN")
    print(f"Fee-free cash remaining: {free_remaining:.2f} AZN")
    print(f"Outgoing transfers:     {outgoing_transfers}/5")


def deposit_money(username, current_balance, today_deposits, atm_cash):
    """06. Cash deposits with a daily deposit limit[cite: 6]"""
    DAILY_LIMIT = 2000.00
    
    print(f"Deposited today: {today_deposits:.2f} AZN")
    print(f"Daily deposit maximum: {DAILY_LIMIT:.2f} AZN")
    print(f"Remaining deposit allowance: {DAILY_LIMIT - today_deposits:.2f} AZN")
    
    try:
        amount_str = input("Requested deposit: ")
        amount = float(amount_str)
        
        if amount <= 0:
            print("\nDeposit declined: amount must be greater than zero[cite: 6, 15].")
            return current_balance, today_deposits, atm_cash
            
        if '.' in amount_str and len(amount_str.split('.')[1]) > 2:
            print("\nDeposit declined: maximum two decimal places allowed[cite: 6, 15].")
            return current_balance, today_deposits, atm_cash

        if today_deposits + amount > DAILY_LIMIT:
            print("\nDeposit declined: daily limit would be exceeded[cite: 6, 15].")
            print("Account balance and ATM cash remain unchanged[cite: 6, 7, 15].")
            return current_balance, today_deposits, atm_cash

        current_balance += amount
        today_deposits += amount
        atm_cash += amount

        print(f"\nDeposit successful! Deposited: {amount:.2f} AZN")
        print(f"New account balance: {current_balance:.2f} AZN")
        
        return current_balance, today_deposits, atm_cash

    except ValueError:
        print("\nDeposit declined: please enter a valid number format[cite: 15].")
        return current_balance, today_deposits, atm_cash


def withdraw_money(username, current_balance, today_withdrawals, atm_cash):
    """07. Cash withdrawals, fees and daily limits[cite: 7]"""
    FREE_ALLOWANCE = 500.00
    DAILY_MAX = 1000.00
    FEE_RATE = 0.02
    
    print(f"Cash withdrawn earlier today: {today_withdrawals:.2f} AZN")
    print(f"Daily withdrawal maximum: {DAILY_MAX:.2f} AZN")
    print(f"Remaining daily allowance: {DAILY_MAX - today_withdrawals:.2f} AZN")
    
    try:
        amount_str = input("New withdrawal request: ")
        amount = float(amount_str)
        
        if amount <= 0:
            print("\nWithdrawal declined: amount must be greater than zero[cite: 7, 15].")
            return current_balance, today_withdrawals, atm_cash
            
        if '.' in amount_str and len(amount_str.split('.')[1]) > 2:
            print("\nWithdrawal declined: maximum two decimal places allowed[cite: 7, 15].")
            return current_balance, today_withdrawals, atm_cash

        if today_withdrawals + amount > DAILY_MAX:
            print(f"\nWithdrawal declined: absolute daily maximum (1,000.00 AZN) would be exceeded[cite: 7, 15].")
            print(f"The remaining cash withdrawal allowance is {DAILY_MAX - today_withdrawals:.2f} AZN[cite: 7].")
            print("Account balance and ATM cash remain unchanged[cite: 7, 15].")
            return current_balance, today_withdrawals, atm_cash

        if atm_cash < amount:
            print("\nWithdrawal declined: the shared ATM reserve must contain enough cash[cite: 7, 8, 15].")
            return current_balance, today_withdrawals, atm_cash

        if today_withdrawals >= FREE_ALLOWANCE:
            charged_at_2 = amount
        else:
            remaining_free = FREE_ALLOWANCE - today_withdrawals
            charged_at_2 = max(0.0, amount - remaining_free)
            
        commission = charged_at_2 * FEE_RATE
        total_deduction = amount + commission

        if current_balance < total_deduction:
            print("\nWithdrawal declined: account balance must cover both requested cash and withdrawal commission[cite: 7, 15].")
            return current_balance, today_withdrawals, atm_cash

        current_balance -= total_deduction
        today_withdrawals += amount 
        atm_cash -= amount

        if charged_at_2 > 0:
            print(f"Remaining fee-free allowance: {max(0.0, FREE_ALLOWANCE - (today_withdrawals - amount)):.2f} AZN")
            print(f"Amount charged at 2%: {charged_at_2:.2f} AZN")
            print(f"Withdrawal commission: {commission:.2f} AZN")
        
        print(f"Amount deducted from account: {total_deduction:.2f} AZN")
        print(f"Cash paid out: {amount:.2f} AZN")
        print(f"New account balance: {current_balance:.2f} AZN")
        
        return current_balance, today_withdrawals, atm_cash

    except ValueError:
        print("\nWithdrawal declined: please enter a valid number format[cite: 15].")
        return current_balance, today_withdrawals, atm_cash