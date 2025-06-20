import sys, re

from src.model.coworking_model import Coworking, User


class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking

    def print_menu(self):
        if self.coworking.is_current_user_exists():
            print("1. Show all seats")
            print("2. Show all reserved seats")
            print("3. Reserve seat")
            print("4. Cancel seat reservation")
            print("5. Logout")
            print("6. Exit")
        else:
            print("1. Registration")
            print("2. Login")
            print("3. Exit")

    def handle_menu_option(self, option):
        if self.coworking.is_current_user_exists():
            if option == "1":
                return self.handle_show_seats_option()
            elif option == "2":
                self.handle_show_reserved_seats_option()
            elif option == "3":
                self.handle_reserve_seat_option()
            elif option == "4":
                self.handle_cancel_reservation_option()
            elif option == "5":
                self.handle_logout_option()
                return "auto"
            elif option == "6":
                print("Exit.")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
            return "manual"
        else:
            if option == "1":
                self.handle_registration_option()
                return "auto"
            elif option == "2":
                self.handle_login_option()
            elif option == "3":
                print("Exit.")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
            return "manual"

    def handle_registration_option(self):
        print(f"\n=== Registration ===")
        while True:
            first_name = input("First name: ").strip()
            if not first_name.isalpha():
                print("First name can contain letters only. Try again.")
            else:
                break

        while True:
            last_name = input("Last name: ").strip()
            if not last_name.isalpha():
                print("Last name can contain letters only. Try again.")
            else:
                break

        while True:
            email = input("Email: ").strip()
            if not re.match(r"^[\w.-]+@[\w.-]+\.\w+$", email):
                print("Invalid email address. Try again.")
            else:
                break

        while True:
            phone = input("Phone number: ").strip()
            if not (phone.isdigit() and len(phone) == 9):
                print("Phone number must contain 9 digits only. Try again.")
            else:
                break

        user = User(first_name, last_name, email, phone)
        self.coworking.register_user(user)
        print(f"\nWelcome, {first_name} {last_name}!")

    def handle_login_option(self):
        print(f"\n=== Login ===")
        while True:
            login = input("Email or Phone number: ").strip()
            if not login:
                print("Login cannot be empty. Please try again or type 'r' to return to the main menu.")
                continue
            elif login.lower() == "r":
                return
            user = self.coworking.login_user(login)
            if user:
                print(f"\nWelcome, {user.first_name} {user.last_name}!")
                break
            else:
                print("User not found. Please try again or type 'r' to return to the main menu.")

    def handle_logout_option(self):
        self.coworking.logout_user()
        print("You have been logged out.")

    def handle_show_seats_common(self, display_function):
        while True:
            floor_numbers = [floor.number for floor in self.coworking.floors]
            option = input(f"Please select floor number {floor_numbers} or print 'r' to return to the main menu: ")
            if option.lower() == "r":
                return "auto"
            try:
                floor_number = int(option)
                floor = self.coworking.find_floor(floor_number)
                if floor:
                    display_function(floor)
                else:
                    print(f"Invalid floor number.")
            except ValueError:
                print("Invalid input.")

    def handle_show_seats_option(self):
        self.handle_show_seats_common(self.print_floor)

    def handle_show_reserved_seats_option(self):
        self.handle_show_seats_common(self.print_reserved_seats)

    def handle_reserve_seat_option(self):
        self.coworking.reserve_seat()

    def handle_cancel_reservation_option(self):
        self.coworking.cancel_seat_reservation()

    @staticmethod
    def print_floor(floor):
        print(f"       =======  Floor {floor.number}  =======    ")
        for i, seat in enumerate(floor.seats, 1):
            print(f"{seat.number:>3}({'X' if seat.reserved else 'O'})", end="  ")
            if i % 5 == 0:
                print()
        print()

    @staticmethod
    def print_reserved_seats(floor):
        print(f"   ======= Reserved Seats on Floor {floor.number} =======")
        reserved_seats = [seat for seat in floor.seats if seat.reserved]

        if not reserved_seats:
            print("No seats are currently reserved on this floor.")
            return

        for i, seat in enumerate(reserved_seats, 1):
            print(f"{seat.number:>3}(X)", end="  ")
            if i % 5 == 0:
                print()
        print()

    def start(self):
        print("Welcome to the Coworking Space Reservation System!")
        while True:
            self.print_menu()
            selected_option = input("Select an option: ")
            status = self.handle_menu_option(selected_option)
            if status == "auto":
                continue
            else:
                is_continue = input("Do you want to continue? (y/n): ")
                if is_continue.strip().lower() != "y":
                    break
