
class Coworking:
    def __init__(self, floors):
        self.floors = floors

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





