import sys
from controllers.coworking_controller import CoworkingController
from models.coworking_model import Seat, Floor


class ConsoleCoworkingApp:
    def __init__(self, controller: CoworkingController):
        self.controller = controller

    @staticmethod
    def print_menu():
        print("\n--- Menu ---")
        print("1. Show all seats")
        print("2. Reserve seat")
        print("3. Cancel reservation")
        print("4. Save to JSON")
        print("5. Load from JSON")
        print("6. Show available seats (filtered)")
        print("7. Exit")

    def handle_menu_option(self, option):
        if option == "1":
            return self.handle_show_seats_option()
        elif option == "2":
            self.handle_reserve_seat_option()
        elif option == "3":
            self.handle_cancel_reservation_option()
        elif option == "4":
            self.handle_save_to_json_option()
        elif option == "5":
            self.handle_load_from_json_option()
        elif option == "6":
            self.handle_show_available_seats_option()
        elif option == "7":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")
        return "manual"

    def handle_show_seats_option(self):
        while True:
            floor_numbers = self.controller.get_all_floor_numbers()
            option = input(f"Select floor number {floor_numbers} or type 'r' to return to the main menu: ")

            if option.lower() == "r":
                return "auto"
            else:
                try:
                    floor = self.controller.show_all_seats(int(option))
                    if floor is not None:
                        self.print_floor(floor)
                    else:
                        print(f"Invalid floor number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

    def handle_reserve_seat_option(self):
        try:
            floor_num = int(input("Enter floor number to reserve a seat: "))
            seat_num = int(input("Enter seat number to reserve: "))
            reservation_id = input("Enter reservation ID (e.g., your name): ")
            if self.controller.reserve_seat(floor_num, seat_num, reservation_id):
                print(f"Seat number {seat_num} on floor {floor_num} has been reserved.")
            else:
                print(
                    f"Could not reserve seat {seat_num} on floor {floor_num}. It might be already reserved or invalid.")
        except ValueError:
            print("Invalid input. Please enter numbers for floor and seat.")

    def handle_cancel_reservation_option(self):
        try:
            floor_num = int(input("Enter floor number to cancel reservation: "))
            seat_num = int(input("Enter seat number to cancel reservation: "))
            if self.controller.cancel_reservation(floor_num, seat_num):
                print(f"Reservation for seat number {seat_num} on floor {floor_num} has been canceled.")
            else:
                print(
                    f"Could not cancel reservation for seat {seat_num} on floor {floor_num}. It might not be reserved or invalid.")
        except ValueError:
            print("Invalid input. Please enter numbers for floor and seat.")

    def handle_show_available_seats_option(self):
        try:
            floor_num = int(input("Enter floor number to search for seats: "))

            is_docking_station_input = input("Should the seat have a docking station? (y/n/any): ").lower()
            is_docking_station = None
            if is_docking_station_input == 'y':
                is_docking_station = True
            elif is_docking_station_input == 'n':
                is_docking_station = False

            has_2_screens_input = input("Should the seat have 2 screens? (y/n/any): ").lower()
            has_2_screens = None
            if has_2_screens_input == 'y':
                has_2_screens = True
            elif has_2_screens_input == 'n':
                has_2_screens = False

            is_electrical_desk_adjustment_input = input(
                "Should the seat have electrical desk adjustment? (y/n/any): ").lower()
            is_electrical_desk_adjustment = None
            if is_electrical_desk_adjustment_input == 'y':
                is_electrical_desk_adjustment = True
            elif is_electrical_desk_adjustment_input == 'n':
                is_electrical_desk_adjustment = False

            available_seats = self.controller.find_filtered_available_seats(
                floor_num,
                is_docking_station=is_docking_station,
                has_2_screens=has_2_screens,
                is_electrical_desk_adjustment=is_electrical_desk_adjustment
            )

            if available_seats:
                print(f"\nAvailable seats on floor {floor_num} with selected filters:")
                for seat in available_seats:
                    self.print_seat_details(seat)
            else:
                print(f"No available seats on floor {floor_num} with selected filters.")
        except ValueError:
            print("Invalid input. Please enter a number for the floor.")

    def handle_save_to_json_option(self):
        filename = input("Enter the filename to save the coworking data (e.g., coworking.json): ")
        if self.controller.save_coworking_data(filename):
            print(f"Coworking data saved to {filename}")
        else:
            print(f"Failed to save data to {filename}.")

    def handle_load_from_json_option(self):
        filename = input("Enter the filename to load the coworking data from (e.g., coworking.json): ")
        if self.controller.load_coworking_data(filename):
            print(f"Coworking data loaded from {filename}")
        else:
            print(f"Failed to load data from {filename}.")

    @staticmethod
    def print_floor(floor: Floor):
        print(f"\n       =======  Floor {floor.number}  =======    ")
        if not floor.seats:
            print("No seats on this floor.")
            return

        for i, seat in enumerate(floor.seats, 1):
            status = 'X' if seat.is_occupied else 'O'
            details = f" (D:{'T' if seat.is_docking_station else 'F'}, S2:{'T' if seat.has_2_screens else 'F'}, E:{'T' if seat.is_electrical_desk_adjustment else 'F'})"
            print(f"{seat.number:>3}({status}){details}", end="\n" if i % 1 == 0 else "  ")
        print("\n")

    @staticmethod
    def print_seat_details(seat: Seat):
        status = "Occupied" if seat.is_occupied else "Free"
        reservation_id_info = f" (Reservation ID: {seat.reserved_by.reservation_id})" if seat.is_occupied else ""
        print(f"  Seat {seat.number}:")
        print(f"    Status: {status}{reservation_id_info}")
        print(f"    Docking Station: {'Yes' if seat.is_docking_station else 'No'}")
        print(f"    2 Screens: {'Yes' if seat.has_2_screens else 'No (1 screen)'}")
        print(f"    Electrical Desk Adjustment: {'Yes' if seat.is_electrical_desk_adjustment else 'No'}")
        print("-" * 30)

    def start(self):
        print("Welcome to the Coworking Space Reservation System!")
        while True:
            self.print_menu()
            selected_option = input("Select an option: ")
            status = self.handle_menu_option(selected_option)
            if selected_option == "7":
                break
            if status == "auto":
                continue
            else:
                is_continue = input("Do you want to continue? (y/n): ")
                if is_continue.strip().lower() != "y":
                    break