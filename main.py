from auth import change_password, login
from storage import load_data, save_data
from transactions import (
    add_transaction_entry,
    check_balance,
    deposit_money,
    display_account_info,
    display_daily_limits,
    show_transaction_history,
    transfer_money,
    withdraw_money,
)


def initialize_user_defaults(data):
    users = data.get("users", {})
    for user in users.values():
        user.setdefault("status", "active")
        user.setdefault("blocked", False)
        user.setdefault("failed_attempts", 0)
        user.setdefault("lockout_until", None)
        user.setdefault("today_deposits", 0.0)
        user.setdefault("today_withdrawals", 0.0)
        user.setdefault("history", [])
        user.setdefault("daily_transfers", 0)
        user.setdefault("daily_transfer_date", None)
        user.setdefault("last_transaction_time", None)
        user.setdefault("next_txn_id", 1)


def show_main_menu(username):
    print("====================================")
    print(" PYTHON BANKING SYSTEM")
    print("====================================")
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
    print("====================================")


def main():
    data = load_data()
    initialize_user_defaults(data)
    save_data(data)

    while True:
        username = login(data, save_data)
        if username is None:
            print("Exiting system...")
            return

        user = data["users"][username]
        print(f"\nSuccessfully logged in. Welcome, {username}.")

        while True:
            show_main_menu(username)
            choice = input("Select an option: ").strip()

            if choice == "1":
                display_account_info(
                    username=username,
                    account_number=user["account_number"],
                    balance=user["balance"],
                    status=user.get("status", "active"),
                )

            elif choice == "2":
                check_balance(user["balance"])

            elif choice == "3":
                old_balance = user["balance"]
                user["balance"], user["today_deposits"], data["atm_cash"] = deposit_money(
                    username=username,
                    current_balance=user["balance"],
                    today_deposits=user.get("today_deposits", 0.0),
                    atm_cash=data.get("atm_cash", 0.0),
                )
                if user["balance"] > old_balance:
                    add_transaction_entry(
                        user,
                        "deposit",
                        user["balance"] - old_balance,
                        "cash deposit",
                    )
                save_data(data)

            elif choice == "4":
                old_balance = user["balance"]
                user["balance"], user["today_withdrawals"], data["atm_cash"] = withdraw_money(
                    username=username,
                    current_balance=user["balance"],
                    today_withdrawals=user.get("today_withdrawals", 0.0),
                    atm_cash=data.get("atm_cash", 0.0),
                )
                if user["balance"] < old_balance:
                    add_transaction_entry(
                        user,
                        "withdrawal",
                        old_balance - user["balance"],
                        "cash withdrawal",
                    )
                save_data(data)

            elif choice == "5":
                if transfer_money(data, username):
                    save_data(data)

            elif choice == "6":
                show_transaction_history(user)

            elif choice == "7":
                display_daily_limits(
                    today_deposits=user.get("today_deposits", 0.0),
                    today_withdrawals=user.get("today_withdrawals", 0.0),
                    outgoing_transfers=user.get("daily_transfers", 0),
                )

            elif choice == "8":
                if change_password(data, username, save_data):
                    print("Please log in again with your new password.")
                    break

            elif choice == "9":
                print("Logged out successfully.")
                break

            elif choice == "0":
                print("Thank you for using our ATM. Goodbye!")
                return

            else:
                print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()
