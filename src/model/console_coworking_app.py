import sys
import json

from src.model.coworking_model import Coworking


class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking

    @staticmethod
    def print_menu():
        print("1. Show all seats")
        print("2. Reserved seats")
        print("3. Cancel reservation")
        print("4. Save to JSON")
        print("5. Exit")

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
            print("Exit.")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")
        return "manual"

    def handle_show_seats_option(self):
        while True:
            floor_numbers = [floor.number for floor in self.coworking.floors]
            option = input(f"Please select floor number {floor_numbers} or print 'r' to return to the main menu: ")

            if option == "r":
                return "auto"
            else:
                try:
                    floor = self.coworking.find_floor(int(option))
                    if floor is not None:
                        self.print_floor(floor)
                    else:
                        print(f"Invalid floor number.")
                except ValueError:
                    print("Invalid input.")

    def handle_reserve_seat_option(self):
        self.coworking.reserve_seat(1, 1)
        print(f"Seat number {1} on the {1} floor is reserved.")

    def handle_cancel_reservation_option(self):
        self.coworking.cancel_seat_reservation(1, 1)
        print(f"Reservation for seat number {1} on the {1} floor is canceled.")

    def handle_save_to_json_option(self):
        filename = input("Enter the filename to save the coworking data (e.g., coworking.json): ")
        data_to_save = self.serialize_coworking()
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Coworking data saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def serialize_coworking(self):
        floors_data = []
        for floor in self.coworking.floors:
            seats_data = [{"number": seat.number, "reserved": seat.reserved} for seat in floor.seats]
            floors_data.append({"number": floor.number, "seats": seats_data})
        return {"floors": floors_data}

    @staticmethod
    def print_floor(floor):
        print(f"       =======  Floor {floor.number}  =======    ")
        for i, seat in enumerate(floor.seats, 1):
            print(f"{seat.number:>3}({'X' if seat.reserved else 'O'})", end="  ")
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

