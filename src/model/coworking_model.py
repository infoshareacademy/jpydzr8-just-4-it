
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

    def reserve_seat(self, floor_number, seat_number):
        return False

    def cancel_seat_reservation(self, floor_number, seat_number):
        return False

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



