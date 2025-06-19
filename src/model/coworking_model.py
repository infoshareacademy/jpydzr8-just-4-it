class Coworking:
    def __init__(self, floors, users):
        self.floors = floors
        self.users = users
        self.current_user = None

    def login_user(self,login):
        for user in self.users:
            if user.email == login or user.phone == login:
                self.current_user = user
                return user
        return None

    def logout_user(self):
        self.current_user = None

    def register_user(self, user):
        self.users.append(user)
        self.current_user = user

    def is_current_user_exists(self):
        return self.current_user is not None

    def select_floor(self, action_text=""):
        floor_numbers = [str(floor.number) for floor in self.floors]
        while True:
            floor_number_input = input(
                f"Please select floor number {floor_numbers}{action_text} or 'r' to return: ").strip()
            if floor_number_input.lower() == 'r':
                return None
            if floor_number_input not in floor_numbers:
                print(f"Invalid floor number. Please choose from: {', '.join(floor_numbers)}.")
                continue
            floor = self.find_floor(int(floor_number_input))
            if floor:
                return floor
            else:
                print(f"Floor {floor_number_input} does not exist.")

    @staticmethod
    def select_seat(floor, action="select"):
        while True:
            seat_input = input(
                f"Please {action} seat number (1 to {len(floor.seats)}) or 'r' to return: ").strip()
            if seat_input.lower() == 'r':
                return None
            try:
                seat_number = int(seat_input)
                if 1 <= seat_number <= len(floor.seats):
                    return floor.seats[seat_number - 1], seat_number
                else:
                    print(f"Invalid seat number. Must be between 1 and {len(floor.seats)}.")
            except ValueError:
                print("Invalid input. Please enter a numeric seat number.")

    def reserve_seat(self):
        floor = self.select_floor()
        if not floor:
            return

        result = self.select_seat(floor, "reserve")
        if not result:
            return

        seat, seat_number = result
        if seat.reserved:
            print(f"Seat number {seat_number} on floor {floor.number} is already reserved.")
            return

        seat.reserved = True
        print(f"Seat number {seat_number} on floor {floor.number} is now reserved.")

    def cancel_seat_reservation(self):
        floor = self.select_floor(" to cancel reservation")
        if not floor:
            return

        result = self.select_seat(floor, "cancel")
        if not result:
            return

        seat, seat_number = result
        if not seat.reserved:
            print(f"Seat number {seat_number} on floor {floor.number} is not currently reserved.")
            return

        seat.reserved = False
        print(f"Reservation for seat number {seat_number} on floor {floor.number} has been canceled.")

    def find_floor(self, floor_number):
        for floor in self.floors:
            if floor.number == floor_number:
                return floor
        return None

class Floor:
    def __init__(self, number, number_of_seats):
        self.number = number
        self.seats = self.generate_seats(number_of_seats)

    @staticmethod
    def generate_seats(number_of_seats):
        return [Seat(num, False) for num in range(1, number_of_seats + 1)]


class Seat:
    def __init__(self, number, reserved):
        self.number = number
        self.reserved = reserved

class User:
    def __init__(self, first_name: object, last_name: object, email: object, phone: object) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone



