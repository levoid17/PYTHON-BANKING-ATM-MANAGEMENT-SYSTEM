from auth import change_password, login
from storage import load_data, save_data
from transactions import (
    deposit_money,
    display_account_info,
    display_daily_limits,
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
    print(f"\nSuccessfully logged in. Welcome, {username}.")

    while True:
        print("\n--- MAIN MENU ---")
        print("1. View Account Information")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. View Daily Limits")
        print("5. Change Password")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            display_account_info(
                username=username,
                account_number=user["account_number"],
                balance=user["balance"],
                status=user.get("status", "active"),
            )

        elif choice == "2":
            user["balance"], user["today_deposits"], data["atm_cash"] = deposit_money(
                username=username,
                current_balance=user["balance"],
                today_deposits=user.get("today_deposits", 0.0),
                atm_cash=data.get("atm_cash", 0.0),
            )
            save_data(data)

        elif choice == "3":
            user["balance"], user["today_withdrawals"], data["atm_cash"] = withdraw_money(
                username=username,
                current_balance=user["balance"],
                today_withdrawals=user.get("today_withdrawals", 0.0),
                atm_cash=data.get("atm_cash", 0.0),
            )
            save_data(data)

        elif choice == "4":
            display_daily_limits(
                today_deposits=user.get("today_deposits", 0.0),
                today_withdrawals=user.get("today_withdrawals", 0.0),
                outgoing_transfers=user.get("daily_transfers", 0),
            )

        elif choice == "5":
            if change_password(data, username, save_data):
                print("Please log in again with your new password.")
                break

        elif choice == "6":
            print("Thank you for using our ATM. Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 6.")


if __name__ == "__main__":
    main()
