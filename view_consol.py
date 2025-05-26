def view_available_desks(self):
    print("\n=== AVAILABLE DESKS ===")
    for floor in self.controller.get_all_floors():
        seats_view = ' '.join(str(seat) for seat in floor.seats)
        print(f"Floor {floor.number}: {seats_view}")

class Seat:
    def __init__(self, number, is_reserved=False):
        self.number = number
        self.is_reserved = is_reserved

    def __str__(self):
        return "X" if self.is_reserved else str(self.number)
