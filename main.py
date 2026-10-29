from storage import load_data, save_data
from auth import login, change_password
from transactions import (
    display_account_info, 
    deposit_money, 
    withdraw_money, 
    display_daily_limits
)

def main():
    # 1. Load data before starting the program
    data = load_data()

    print("=== Welcome to VTB ATM ===")

    # 2. Login process
    username = login(data, save_data)

    if username is None:
        print("Exiting system...")
        return

    # Find the current user object
    user = data["users"][username]
    print(f"\nSuccessfully logged in! Welcome, {username}.")

    # 3. Main ATM Menu (While loop)
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
                status=user.get("status", "Active")
            )

        elif choice == "2":
            # Update user balance, today's deposits, and ATM cash with the returned values
            user["balance"], user["today_deposits"], data["atm_cash"] = deposit_money(
                username=username,
                current_balance=user["balance"],
                today_deposits=user["today_deposits"],
                atm_cash=data.get("atm_cash", 5000.00)
            )
            # Save changes immediately to storage
            save_data(data)

        elif choice == "3":
            # Update user balance, today's withdrawals, and ATM cash with the returned values
            user["balance"], user["today_withdrawals"], data["atm_cash"] = withdraw_money(
                username=username,
                current_balance=user["balance"],
                today_withdrawals=user["today_withdrawals"],
                atm_cash=data.get("atm_cash", 5000.00)
            )
            # Save changes immediately to storage
            save_data(data)

        elif choice == "4":
            display_daily_limits(
                today_deposits=user["today_deposits"], 
                today_withdrawals=user["today_withdrawals"]
            )

        elif choice == "5":
            success = change_password(data, username, save_data)
            if success:
                print("Please log in again with your new password.")
                break

        elif choice == "6":
            print("Thank you for using our ATM. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number between 1 and 6.")

if __name__ == "__main__":
    main()