import sys
import re

from src.model.coworking_model import Coworking, User


class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking


    def print_menu(self):
        if self.coworking.is_current_user_exists():
            print("1. Show all seats")
            print("2. Show all reserved seats")
            print("3. Check seat availability")
            print("4. Reserve seat")
            print("5. Cancel seat reservation")
            print("6. Save data to json")
            print("7. Load data from json")
            print("8. Filter by seat enhancements")
            print("9. Logout")
            print("10. Exit")
        else:
            print("1. Registration")
            print("2. Login")
            print("3. Load user and seats from JSON")
            print("4. Exit")


    def handle_menu_option(self, option):
        if self.coworking.is_current_user_exists():
            if option == "1":
                return self.handle_show_seats_option()
            elif option == "2":
                self.handle_show_reserved_seats_option()
            elif option == "3":
                self.check_seat_availability_option()
            elif option == "4":
                self.handle_reserve_seat_option()
            elif option == "5":
                self.handle_cancel_reservation_option()
            elif option == "6":
                self.handle_save_data_option()
            elif option == "7":
                self.handle_load_data_option()
            elif option == "8":
                self.handle_filter_by_enhancement()
            elif option == "9":
                self.handle_logout_option()
                return "auto"
            elif option == "10":
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
                self.handle_load_data_option(unregistered=True)
                return "auto"
            elif option == "4":
                print("Exit.")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
            return "manual"


    @staticmethod
    def show_legend(all_legend=True):
        print("----------------------------------------------------------------------------------------------")
        answer = input("Show legend? (y/n): ").strip().lower()
        if answer == 'y':
            print("----------------------------------------------------------------------------------------------")
            print("Legend: - how unreserved and reserved seat is denoted:")
            print("Each seat has its number and sign in the brackets, e.g. 1(X)")
            print("Seat with sign 0: e.g. 1(0) - unreserved seat")
            if all_legend:
                print("Seat with sign X: e.g. 1(X) - reserved seat without any enhancements")
                print("Seat with sign D: e.g. 1(D) - reserved seat with docking station")
                print("Seat with sign D: e.g. 1(S) - reserved seat with two screens")
                print("Seat with sign D: e.g. 1(E) - reserved seat with electrical desk adjustment")
                print("Seat with sign with any combination of enhancements e.g. 1(DS) - docking station & two screens")
                print("Seat with sign with any combination of enhancements e.g. 1(DSE) - full: all three enhancements")
            print("----------------------------------------------------------------------------------------------")
        else:
            print("Legend is not shown.")
            print("----------------------------------------------------------------------------------------------")


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
            self.show_legend()
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


    def check_seat_availability_option(self):
        self.coworking.check_seat_availability_option()


    def handle_save_data_option(self):
        while True:
            filename = input("Enter filename (e.g., data.json) or 'r' to return: ").strip()
            if filename.lower() == 'r':
                return
            if not filename.endswith(".json"):
                print("Filename must end with '.json'. Please try again.")
                continue
            self.coworking.save_to_json(filename)
            break


    def handle_load_data_option(self, unregistered=False):
        while True:
            filename = input("Enter filename to load (e.g., data.json) or 'r' to return: ").strip()
            if filename.lower() == 'r':
                return
            if not filename.endswith(".json"):
                print("Filename must end with '.json'. Please try again.")
                continue

            loaded_coworking = Coworking.load_from_json(filename)
            if loaded_coworking:
                old_user = self.coworking.current_user

                self.coworking = loaded_coworking
                print(f"Data loaded successfully from {filename}.")

                if old_user:
                    matched_user = next(
                        (user for user in self.coworking.users
                         if user.email == old_user.email and user.phone == old_user.phone),
                        None
                    )
                    if matched_user:
                        self.coworking.current_user = matched_user
                        print(f"Welcome back, {matched_user.first_name}!")
                    else:
                        self.coworking.current_user = None
                        print("Your previous user session could not be restored.")

                elif self.coworking.users and unregistered:
                    print("Do you want to log in as one of the loaded users?")
                    while True:
                        answer = input("Login now? (y/n): ").strip().lower()
                        if answer == 'y':
                            login = input("Enter email or phone: ").strip()
                            user = self.coworking.login_user(login)
                            if user:
                                print(f"Welcome, {user.first_name} {user.last_name}!")
                            else:
                                print("User not found in loaded data.")
                            break
                        elif answer == 'n':
                            break
                        else:
                            print("Please enter 'y' or 'n'.")
                break


    @staticmethod
    def display_matching_seats(matching_seats_per_floor, label):
        any_matches = False
        for floor, seats in matching_seats_per_floor:
            if seats:
                any_matches = True
                print(f"\nFloor {floor.number} - {label}:")
                for i, seat in enumerate(seats, 1):
                    print(f"{seat.number:>3}(O)", end="  ")
                    if i % 5 == 0:
                        print()
                print()
        if not any_matches:
            print("No available seats were found.")


    def filter_no_enhancements(self):
        matching_seats_per_floor = [
            (floor, [seat for seat in floor.seats
                     if not seat.is_docking_station and not seat.has_2_screens
                     and not seat.is_electrical_desk_adjustment and not seat.reserved])
            for floor in self.coworking.floors
        ]
        self.display_matching_seats(matching_seats_per_floor, label="Matching available seats")


    def handle_filter_by_enhancement(self):
        self.show_legend(all_legend=False)
        print("\nFilter by enhancements:")
        print("D - Docking Station")
        print("S - Dual Screens")
        print("E - Electrical Desk Adjustment")
        print("X - No enhancements (i.e., no D, S, or E)")

        user_input = input("Enter enhancement codes (e.g., D, DS, DSE, or X): ").strip().upper()

        valid_inputs = {"D", "S", "E", "DS", "DE", "SE", "DSE", "X"}
        if not user_input or not all(c in "DSEX" for c in user_input):
            print("Invalid input. Please enter a combination of D, S, E, or X.")
            return

        if "X" in user_input:
            self.filter_no_enhancements()
            return

        enhancement_attributes = {
            "D": "is_docking_station",
            "S": "has_2_screens",
            "E": "is_electrical_desk_adjustment"
        }

        selected_attrs = [enhancement_attributes[c] for c in user_input if c in enhancement_attributes]

        matching_seats_per_floor = []
        for floor in self.coworking.floors:
            matching_seats = []
            for seat in floor.seats:
                if not seat.reserved and all(getattr(seat, attr) for attr in selected_attrs):
                    matching_seats.append(seat)
            matching_seats_per_floor.append((floor, matching_seats))

        self.display_matching_seats(matching_seats_per_floor, label="Matching available seats")



    @staticmethod
    def print_floor(floor):
        print(f"       =======  Floor {floor.number}  =======    ")
        for i, seat in enumerate(floor.seats, 1):
            symbol = "O"
            if seat.reserved:
                if seat.is_docking_station and seat.has_2_screens and seat.is_electrical_desk_adjustment:
                    symbol = "DSE"
                elif seat.is_docking_station and seat.has_2_screens:
                    symbol = "DS"
                elif seat.is_docking_station and seat.is_electrical_desk_adjustment:
                    symbol = "DE"
                elif seat.has_2_screens and seat.is_electrical_desk_adjustment:
                    symbol = "SE"
                elif seat.is_docking_station:
                    symbol = "D"
                elif seat.has_2_screens:
                    symbol = "S"
                elif seat.is_electrical_desk_adjustment:
                    symbol = "E"
                else:
                    symbol = "X"
            print(f"{f'{seat.number}({symbol})':<11}", end="")
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
            symbol = "X"
            if seat.is_docking_station and seat.has_2_screens and seat.is_electrical_desk_adjustment:
                symbol = "DSE"
            elif seat.is_docking_station and seat.has_2_screens:
                symbol = "DS"
            elif seat.is_docking_station and seat.is_electrical_desk_adjustment:
                symbol = "DE"
            elif seat.has_2_screens and seat.is_electrical_desk_adjustment:
                symbol = "SE"
            elif seat.is_docking_station:
                symbol = "D"
            elif seat.has_2_screens:
                symbol = "S"
            elif seat.is_electrical_desk_adjustment:
                symbol = "E"
            print(f"{seat.number:>3}({symbol})", end="  ")
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
                while True:
                    is_continue = input("Do you want to continue? (y/n): ").strip().lower()
                    if is_continue == 'y':
                        break
                    elif is_continue == 'n':
                        return
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
