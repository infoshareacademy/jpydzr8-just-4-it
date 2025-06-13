import json


class Reservation:
    def __init__(self, reservation_id: str):
        self.reservation_id = reservation_id

    def to_dict(self):
        return {"reservation_id": self.reservation_id}

    @staticmethod
    def from_dict(data):
        return Reservation(data["reservation_id"])


class Seat:
    def __init__(self, number: int, is_docking_station: bool = False, has_2_screens: bool = False,
                 is_electrical_desk_adjustment: bool = False):
        self.number = number
        self.reserved_by: Reservation | None = None
        self.is_docking_station = is_docking_station
        self.has_2_screens = has_2_screens
        self.is_electrical_desk_adjustment = is_electrical_desk_adjustment

    @property
    def is_occupied(self):
        return self.reserved_by is not None

    def reserve(self, reservation_id: str):
        if not self.is_occupied:
            self.reserved_by = Reservation(reservation_id)
            return True
        return False

    def cancel_reservation(self):
        if self.is_occupied:
            self.reserved_by = None
            return True
        return False

    def to_dict(self):
        return {
            "number": self.number,
            "reserved_by": self.reserved_by.to_dict() if self.reserved_by else None,
            "is_docking_station": self.is_docking_station,
            "has_2_screens": self.has_2_screens,
            "is_electrical_desk_adjustment": self.is_electrical_desk_adjustment,
        }

    @staticmethod
    def from_dict(data):
        seat = Seat(
            data["number"],
            data.get("is_docking_station", False),
            data.get("has_2_screens", False),
            data.get("is_electrical_desk_adjustment", False),
        )
        if data.get("reserved_by"):
            seat.reserved_by = Reservation.from_dict(data["reserved_by"])
        return seat


class Floor:
    def __init__(self, number: int):
        self.number = number
        self.seats: list[Seat] = []

    def add_seat(self, seat: Seat):
        self.seats.append(seat)

    def find_seat(self, seat_number: int) -> Seat | None:
        for seat in self.seats:
            if seat.number == seat_number:
                return seat
        return None


class Coworking:
    def __init__(self):
        self.floors: list[Floor] = []

    def add_floor(self, floor: Floor):
        self.floors.append(floor)

    def find_floor(self, floor_number: int) -> Floor | None:
        for floor in self.floors:
            if floor.number == floor_number:
                return floor
        return None

    def reserve_seat(self, floor_num: int, seat_num: int, reservation_id: str = "default_reservation") -> bool:
        floor = self.find_floor(floor_num)
        if floor:
            seat = floor.find_seat(seat_num)
            if seat:
                return seat.reserve(reservation_id)
        return False

    def cancel_seat_reservation(self, floor_num: int, seat_num: int) -> bool:
        floor = self.find_floor(floor_num)
        if floor:
            seat = floor.find_seat(seat_num)
            if seat:
                return seat.cancel_reservation()
        return False

    def find_available_seats(self, floor_num: int, is_docking_station: bool | None = None,
                             has_2_screens: bool | None = None, is_electrical_desk_adjustment: bool | None = None) -> \
    list[Seat]:
        floor = self.find_floor(floor_num)
        if not floor:
            return []

        available_seats = []
        for seat in floor.seats:
            if not seat.is_occupied:
                match = True
                if is_docking_station is not None and seat.is_docking_station != is_docking_station:
                    match = False
                if has_2_screens is not None and seat.has_2_screens != has_2_screens:
                    match = False
                if is_electrical_desk_adjustment is not None and seat.is_electrical_desk_adjustment != is_electrical_desk_adjustment:
                    match = False

                if match:
                    available_seats.append(seat)
        return available_seats