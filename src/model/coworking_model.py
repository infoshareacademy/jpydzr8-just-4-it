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

    def get_selected_seat(self, action_desc="", seat_action=""):
        floor = self.select_floor(action_desc)
        if not floor:
            return None, None, None

        result = self.select_seat(floor, seat_action)
        if not result:
            return None, None, None

        seat, seat_number = result
        return floor, seat, seat_number

    def reserve_seat(self):
        floor, seat, seat_number = self.get_selected_seat("", "reserve")
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
    @staticmethod
    def generate_seats(self, number_of_seats):
        return [Seat(num, False) for num in range(1, number_of_seats + 1)]


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



