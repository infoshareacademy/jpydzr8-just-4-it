def handle_menu_option(self, option):
    if option == "1":
        self.view_available_desks()
    elif option == "2":
        self.book_desk()
    elif option == "3":
        print("Cancel booking...")
    elif option == "4":
        print("Exit.")
        sys.exit(0)
    else:
        print("Wrong option.")



def book_desk(self):
    try:
        floor_number = int(input("Enter floor number (4-7): "))
        seat_number = int(input("Enter seat number: "))
        success = self.controller.reserve_seat(floor_number, seat_number)
        if success:
            print(f"Seat {seat_number} on floor {floor_number} has been reserved.")
        else:
            print("Seat already reserved or does not exist.")
    except ValueError:
        print("Invalid input.")
