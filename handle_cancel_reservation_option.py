class Coworking:
    def __init__(self, floors, users=None):
        self.floors = floors
        self.users = users or []

    def reserve_seat(self, floor_number, seat_number):
        floor = self.find_floor(floor_number)
        if floor:
            for seat in floor.seats:
                if seat.number == seat_number and not seat.reserved:
                    seat.reserved = True
                    return True
        return False

    def cancel_seat_reservation(self, floor_number, seat_number):
        floor = self.find_floor(floor_number)
        if floor:
            for seat in floor.seats:
                if seat.number == seat_number and seat.reserved:
                    seat.reserved = False
                    return True
        return False

    def find_floor(self, floor_number):
        for floor in self.floors:
            if floor.number == floor_number:
                return floor
        return None



def handle_cancel_reservation_option(self):
    try:
        floor_number = int(input("Enter floor number: "))
        seat_number = int(input("Enter seat number to cancel: "))
        success = self.coworking.cancel_seat_reservation(floor_number, seat_number)
        if success:
            print(f"Reservation for seat number {seat_number} on floor {floor_number} has been canceled.")
        else:
            print("Seat is not reserved or does not exist.")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")

def handle_reserve_seat_option(self):
    try:
        floor_number = int(input("Enter floor number: "))
        seat_number = int(input("Enter seat number to reserve: "))
        success = self.coworking.reserve_seat(floor_number, seat_number)
        if success:
            print(f"Seat number {seat_number} on floor {floor_number} is now reserved.")
        else:
            print("Seat is already reserved or does not exist.")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
