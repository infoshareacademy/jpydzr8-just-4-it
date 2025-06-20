import json

class Seat:
    def __init__(self, number, reserved):
        self.number = number
        self.reserved = reserved

    def __str__(self):
        return "X" if self.reserved else str(self.number)

class Floor:
    def __init__(self, number, number_of_seats):
        self.number = number
        self.seats = self.generate_seats(number_of_seats)

    @staticmethod
    def generate_seats(number_of_seats):
        return [Seat(num, False) for num in range(1, number_of_seats + 1)]


class Coworking:
    def __init__(self, floors):
        self.floors = floors

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

    def save_to_json(self, filename="coworking_data.json"):
        data = {
            "floors": [
                {
                    "number": floor.number,
                    "seats": [{"number": seat.number, "reserved": seat.reserved} for seat in floor.seats]
                }
                for floor in self.floors
            ]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_json(cls, filename="coworking_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            floors = []
            for floor_data in data["floors"]:
                floor = Floor(floor_data["number"], 0)
                floor.seats = []
                for seat_data in floor_data["seats"]:
                    floor.seats.append(Seat(seat_data["number"], seat_data["reserved"]))
                floors.append(floor)
            return cls(floors)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}. File might be corrupted.")
            return None