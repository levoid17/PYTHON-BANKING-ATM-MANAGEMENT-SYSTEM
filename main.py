from datetime import datetime, date

from auth import change_password, login
from storage import load_data, save_data
from transactions import (
    deposit_money,
    display_account_info,
    display_balance,
    display_daily_limits,
    display_transaction_history,
    reset_daily_counters,
    transfer_money,
    withdraw_money,
)


def initialize_user_defaults(data):
    for user in data.get("users", {}).values():
        user.setdefault("status", "active")
        user.setdefault("blocked", False)
        user.setdefault("failed_attempts", 0)
        user.setdefault("lockout_until", None)
        user.setdefault("today_deposits", 0.0)
        user.setdefault("today_withdrawals", 0.0)
        user.setdefault("daily_transfers", 0)
        user.setdefault("daily_reset_date", date.today().isoformat())
        user.setdefault("history", [])
        user.setdefault("next_txn_id", len(user["history"]) + 1)


def _show_menu(username):
    print("\nPYTHON BANKING SYSTEM")
    print(f"Welcome, {username}!")
    print("1. View Account Information")
    print("2. Check Balance")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Transfer Money")
    print("6. Transaction History")
    print("7. Daily Limits")
    print("8. Change Password")
    print("9. Logout")
    print("0. Exit")


def main():
    data = load_data()
    initialize_user_defaults(data)
    save_data(data)

    print("=== Welcome to VTB ATM ===")
    username = login(data, save_data)
    if username is None:
        print("Exiting system...")
        return

    user = data["users"][username]
    reset_daily_counters(user)
    user["last_login"] = datetime.now().isoformat(timespec="seconds")
    save_data(data)
    print(f"\nSuccessfully logged in. Welcome, {username}.")

    while True:
        _show_menu(username)
        choice = input("Select an option: ").strip()

        if choice == "1":
            display_account_info(
                username, user["account_number"], user["balance"], user.get("status", "active")
            )
        elif choice == "2":
            display_balance(user["balance"])
        elif choice == "3":
            user["balance"], user["today_deposits"], data["atm_cash"] = deposit_money(
                username, user["balance"], user["today_deposits"], data.get("atm_cash", 0.0), user
            )
            save_data(data)
        elif choice == "4":
            user["balance"], user["today_withdrawals"], data["atm_cash"] = withdraw_money(
                username,
                user["balance"],
                user["today_withdrawals"],
                data.get("atm_cash", 0.0),
                user,
            )
            save_data(data)
        elif choice == "5":
            if transfer_money(data, username):
                save_data(data)
        elif choice == "6":
            display_transaction_history(user)
        elif choice == "7":
            display_daily_limits(
                user["today_deposits"], user["today_withdrawals"], user["daily_transfers"]
            )
        elif choice == "8":
            if change_password(data, username, save_data):
                print("Please log in again with your new password.")
                break
        elif choice == "9":
            print("You have been logged out.")
            break
        elif choice == "0":
            print("Thank you for using our ATM. Goodbye!")
            return
        else:
            print("Invalid choice. Please select a number between 0 and 9.")


if __name__ == "__main__":
    main()
