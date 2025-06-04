import sys
import json

from model.coworking_model import Coworking, Floor, Seat


class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking

    @staticmethod
    def print_menu():
        print("1. Show all seats")
        print("2. Reserve seat")
        print("3. Cancel reservation")
        print("4. Save to JSON")
        print("5. Load from JSON")
        print("6. Exit")

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

        try:
            floor_num = int(input("Enter floor number to reserve a seat: "))
            seat_num = int(input("Enter seat number to reserve: "))
            if self.coworking.reserve_seat(floor_num, seat_num):
                print(f"Seat number {seat_num} on floor {floor_num} is reserved.")
            else:
                print(
                    f"Could not reserve seat {seat_num} on floor {floor_num}. It might be already reserved or invalid.")
        except ValueError:
            print("Invalid input. Please enter numbers for floor and seat.")

    def handle_cancel_reservation_option(self):

        try:
            floor_num = int(input("Enter floor number to cancel reservation: "))
            seat_num = int(input("Enter seat number to cancel reservation: "))
            if self.coworking.cancel_seat_reservation(floor_num, seat_num):
                print(f"Reservation for seat number {seat_num} on floor {floor_num} is canceled.")
            else:
                print(
                    f"Could not cancel reservation for seat {seat_num} on floor {floor_num}. It might not be reserved or invalid.")
        except ValueError:
            print("Invalid input. Please enter numbers for floor and seat.")

    def handle_save_to_json_option(self):
        filename = input("Enter the filename to save the coworking data (e.g., coworking.json): ")
        data_to_save = self.serialize_coworking()
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Coworking data saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def handle_load_from_json_option(self):
        filename = input("Enter the filename to load the coworking data from (e.g., coworking.json): ")
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.deserialize_coworking(data)
            print(f"Coworking data loaded from {filename}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{filename}'. Check file format.")
        except Exception as e:
            print(f"Error loading from file: {e}")

    def serialize_coworking(self):
        floors_data = []
        for floor in self.coworking.floors:
            seats_data = [{"number": seat.number, "reserved": seat.reserved} for seat in floor.seats]
            floors_data.append({"number": floor.number, "seats": seats_data})
        return {"floors": floors_data}

    def deserialize_coworking(self, data):

        self.coworking.floors = []
        for floor_data in data.get("floors", []):
            floor_number = floor_data.get("number")
            seats_data = floor_data.get("seats", [])


            new_floor = Floor(floor_number)


            for seat_data in seats_data:
                seat_number = seat_data.get("number")
                seat_reserved = seat_data.get("reserved")
                new_seat = Seat(seat_number)
                new_seat.reserved = seat_reserved
                new_floor.seats.append(new_seat)

            self.coworking.floors.append(new_floor)

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
                if selected_option not in ["5", "6"]:  # Don't ask to continue after exit or load
                    is_continue = input("Do you want to continue? (y/n): ")
                    if is_continue.strip().lower() != "y":
                        break