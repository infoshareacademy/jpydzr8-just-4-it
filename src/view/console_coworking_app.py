import sys

from src.model.coworking_model import Coworking


class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking
        self.data_file = "coworking_data.json"

    @staticmethod
    def print_menu():
        print("1. Show all seats")
        print("2. Reserve a seat")
        print("3. Cancel reservation")
        print("4. Save data")
        print("5. Exit")

    def handle_menu_option(self, option):
        if option == "1":
            return self.handle_show_seats_option()
        elif option == "2":
            self.handle_reserve_seat_option()
            self.coworking.save_to_json(self.data_file)
        elif option == "3":
            self.handle_cancel_reservation_option()
            self.coworking.save_to_json(self.data_file)
        elif option == "4":
            self.coworking.save_to_json(self.data_file)
            print("Data saved successfully.")
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
        try:
            floor_number = int(input("Enter floor number to reserve: "))
            seat_number = int(input("Enter seat number to reserve: "))
            success = self.coworking.reserve_seat(floor_number, seat_number)
            if success:
                print(f"Seat number {seat_number} on floor {floor_number} is now reserved.")
            else:
                print("Seat is already reserved or does not exist.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def handle_cancel_reservation_option(self):
        try:
            floor_number = int(input("Enter floor number to cancel reservation: "))
            seat_number = int(input("Enter seat number to cancel reservation: "))
            success = self.coworking.cancel_seat_reservation(floor_number, seat_number)
            if success:
                print(f"Reservation for seat number {seat_number} on floor {floor_number} has been canceled.")
            else:
                print("Seat is not reserved or does not exist.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

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