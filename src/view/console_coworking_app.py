import sys

from src.model.coworking_model import Coworking


# Consolowe przedstawienie aplikacji.
class ConsoleCoworkingApp:
    def __init__(self, coworking: Coworking):
        self.coworking = coworking

    def print_menu(self):
        print("1. Show all seats")
        print("2. Reserved seats")
        print("3. Cancel reservation")
        print("4. Exit")

    def handle_menu_option(self, option):
        if option == "1":
            self.print_data()
        elif option == "2":
            print("Reserved seats...")
        elif option == "3":
            print("Cancel reservation...")
        elif option == "4":
            print("Exit.")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")

    def print_data(self):
        for floor in self.coworking.floors:
            print(f"Floor {floor.number}:" , end=" ")
            for seat in floor.seats:
                print(f"{seat.number}({'X' if seat.reserved else 'O'})" , end=" ")
            print("")

    def start(self):
        print("Welcome to the Coworking Space Reservation System!")
        while True:
            self.print_menu()
            selected_option = input("Select an option: ")
            self.handle_menu_option(selected_option)
            is_continue = input("Do you want to continue? (y/n): ")
            if is_continue.strip().lower() != "y":
                break

