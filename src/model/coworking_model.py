
class Coworking:
    def __init__(self, floors):
        self.floors = floors


class Floor:
    def __init__(self, number, number_of_seats):
        self.number = number
        self.seats = self.generate_seats(number_of_seats)

    def generate_seats(self, number_of_seats):
        return [Seat(num, False) for num in range(1, number_of_seats + 1)]


class Seat:
    def __init__(self, number, reserved):
        self.number = number
        self.reserved = reserved





