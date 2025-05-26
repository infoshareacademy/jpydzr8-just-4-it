

class CoworkingController:
    def __init__(self, coworking):
        self.coworking = coworking

    def reserve_seat(self, floor_number, seat_number):
        return self.coworking.reserve_seat(floor_number, seat_number)

    def get_all_floors(self):
        return self.coworking.floors
