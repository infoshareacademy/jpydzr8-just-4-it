import sys

class ConsoleCoworkingApp:

    def print_menu(self):
        print("1. View available desks")
        print("2. Book a desk")
        print("3. Cancel booking")
        print("4. Exit")

    def handle_menu_option(self, option):
        if option == "1":
            print("View available desks...")
        elif option == "2":
            print("Book a desk...")
        elif option == "3":
            print("Cancel booking...")
        elif option == "4":
            print("Exit.")
            sys.exit(0)
        else:
            print("Wrong option.")

    def start(self):
        print("Welcome to the Coworking Application!")
        while True:
            self.print_menu()
            selected_option = input("Please select an option (1-4): ")
            self.handle_menu_option(selected_option)

            is_continue = input("Do you want to continue (y/n): ")
            if is_continue.strip().lower() != "y":
                break


if __name__ == "__main__":
    app = ConsoleCoworkingApp()
    app.start()