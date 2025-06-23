import json


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

    def get_selected_seat(self, action_desc="", seat_action="", filter_options=None, print_floor_func=None):
        floor = self.select_floor(action_desc)
        if not floor:
            return None, None, None

        seats_to_display = floor.seats
        if filter_options:
            docking = filter_options.get('docking_station')
            screens = filter_options.get('two_screens')
            electrical = filter_options.get('electrical_desk')
            seats_to_display = floor.get_filtered_seats(docking, screens, electrical)
            if not seats_to_display:
                print("No seats match your filter criteria on this floor. Please try different filters or floor.")
                return None, None, None

        while True:
            # Używamy przekazanej funkcji print_floor_func
            if print_floor_func:
                print_floor_func(floor, seats_to_display)
            else:
                # Awaryjnie, jeśli funkcja nie zostanie przekazana
                # Może to być uproszczona wersja drukowania, lub błąd
                print(f"       =======  Floor {floor.number}  =======    ")
                for i, seat in enumerate(seats_to_display, 1):
                    print(f"{seat.number:>3}({'X' if seat.reserved else 'O'})", end="  ")
                    if i % 5 == 0:
                        print()
                print()

            seat_input = input(
                f"Please {seat_action} seat number (1 to {len(floor.seats)}) or 'r' to return: ").strip()
            if seat_input.lower() == 'r':
                return None, None, None
            try:
                seat_number = int(seat_input)
                if 1 <= seat_number <= len(floor.seats):
                    selected_seat_obj = floor.seats[seat_number - 1]
                    if selected_seat_obj in seats_to_display:
                        return floor, selected_seat_obj, seat_number
                    else:
                        print(f"Seat {seat_number} does not match your filter criteria or is not available. Please choose from the displayed seats.")
                else:
                    print(f"Invalid seat number. Must be between 1 and {len(floor.seats)}.")
            except ValueError:
                print("Invalid input. Please enter a numeric seat number.")


    def reserve_seat(self, print_floor_func): # Dodałem print_floor_func
        print("\n--- Seat Reservation ---")
        filter_choice = input("Do you want to apply filters for seat selection? (y/n): ").strip().lower()
        filters = {}
        if filter_choice == 'y':
            filters['docking_station'] = input("Require docking station? (y/n): ").strip().lower() == 'y'
            filters['two_screens'] = input("Require two monitors? (y/n): ").strip().lower() == 'y'
            filters['electrical_desk'] = input("Require electrical desk adjustment? (y/n): ").strip().lower() == 'y'
        else:
            filters = None

        floor, seat, seat_number = self.get_selected_seat("", "reserve", filter_options=filters, print_floor_func=print_floor_func)
        if not seat:
            return

        if seat.reserved:
            print(f"Seat number {seat_number} on floor {floor.number} is already reserved.")
            return

        seat.reserved = True
        print(f"Seat number {seat_number} on floor {floor.number} is now reserved.")


    def cancel_seat_reservation(self):
        floor, seat, seat_number = self.get_selected_seat(" to cancel reservation", "cancel")
        if not seat:
            return

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

    def save_to_json(self, filename):
        data = {
            "floors": [
                {
                    "number": floor.number,
                    "seats": [
                        {
                            "number": seat.number,
                            "reserved": seat.reserved,
                            "is_docking_station": seat.is_docking_station,
                            "has_2_screens": seat.has_2_screens,
                            "is_electrical_desk_adjustment": seat.is_electrical_desk_adjustment,
                        }
                        for seat in floor.seats
                    ]
                }
                for floor in self.floors
            ],
            "users": [
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                }
                for user in self.users
            ]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")

    @classmethod
    def load_from_json(cls, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            floors = []
            for floor_data in data["floors"]:
                floor = Floor(floor_data["number"], 0)
                floor.seats = [
                    Seat(
                        seat_data["number"],
                        seat_data["reserved"],
                        seat_data.get("is_docking_station", False),
                        seat_data.get("has_2_screens", False),
                        seat_data.get("is_electrical_desk_adjustment", False),
                    )
                    for seat_data in floor_data["seats"]
                ]
                floors.append(floor)

            users = []
            for user_data in data["users"]:
                user = User(
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["email"],
                    user_data["phone"],
                )
                users.append(user)

            coworking = cls(floors, users)
            print(f"Data loaded from {filename}")
            return coworking

        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}. Check file format.")
            return None


class Floor:
    def __init__(self, number, number_of_seats):
        self.number = number
        self.seats = self.generate_seats(number_of_seats)

    def generate_seats(self, number_of_seats):
        seats = []
        for num in range(1, number_of_seats + 1):
            is_docking_station = False
            has_2_screens = False
            is_electrical_desk_adjustment = False


            if self.number == 4:
                if num == 1:
                    is_docking_station = True
                elif num == 2:
                    has_2_screens = True
                elif num == 3:
                    is_electrical_desk_adjustment = True
            elif self.number == 5:
                if num == 1:
                    is_docking_station = True
                    has_2_screens = True
                elif num == 2:
                    is_electrical_desk_adjustment = True
                    has_2_screens = True
            elif self.number == 6:
                if num == 1:
                    is_docking_station = True
                    has_2_screens = True
                    is_electrical_desk_adjustment = True

            seats.append(Seat(num, False, is_docking_station, has_2_screens, is_electrical_desk_adjustment))
        return seats

    def get_filtered_seats(self, docking_station=None, two_screens=None, electrical_desk=None):
        filtered_seats = []
        for seat in self.seats:
            match = True
            if docking_station is not None and seat.is_docking_station != docking_station:
                match = False
            if two_screens is not None and seat.has_2_screens != two_screens:
                match = False
            if electrical_desk is not None and seat.is_electrical_desk_adjustment != electrical_desk:
                match = False
            if match:
                filtered_seats.append(seat)
        return filtered_seats


class Seat:
    def __init__(self, number, reserved, is_docking_station=False, has_2_screens=False, is_electrical_desk_adjustment=False):
        self.number = number
        self.reserved = reserved
        self.is_docking_station = is_docking_station
        self.has_2_screens = has_2_screens
        self.is_electrical_desk_adjustment = is_electrical_desk_adjustment

class User:
    def __init__(self, first_name: object, last_name: object, email: object, phone: object) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone



