import json
import sys
from models.coworking_model import Coworking, Floor, Seat, Reservation


class CoworkingController:
    def __init__(self, coworking_model: Coworking):
        self.coworking_model = coworking_model

    def show_all_seats(self, floor_num: int):
        return self.coworking_model.find_floor(floor_num)

    def reserve_seat(self, floor_num: int, seat_num: int, reservation_id: str) -> bool:
        return self.coworking_model.reserve_seat(floor_num, seat_num, reservation_id)

    def cancel_reservation(self, floor_num: int, seat_num: int) -> bool:
        return self.coworking_model.cancel_seat_reservation(floor_num, seat_num)

    def find_filtered_available_seats(self, floor_num: int, is_docking_station: bool | None, has_2_screens: bool | None,
                                      is_electrical_desk_adjustment: bool | None) -> list[Seat]:
        return self.coworking_model.find_available_seats(
            floor_num,
            is_docking_station,
            has_2_screens,
            is_electrical_desk_adjustment
        )

    def get_all_floor_numbers(self) -> list[int]:
        return [floor.number for floor in self.coworking_model.floors]

    def save_coworking_data(self, filename: str) -> bool:
        try:
            floors_data = []
            for floor in self.coworking_model.floors:
                seats_data = [seat.to_dict() for seat in floor.seats]
                floors_data.append({"number": floor.number, "seats": seats_data})
            data_to_save = {"floors": floors_data}

            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False

    def load_coworking_data(self, filename: str) -> bool:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.coworking_model.floors = []
            for floor_data in data.get("floors", []):
                floor_number = floor_data.get("number")
                new_floor = Floor(floor_number)
                for seat_data in floor_data.get("seats", []):
                    new_seat = Seat.from_dict(seat_data)
                    new_floor.seats.append(new_seat)
                self.coworking_model.floors.append(new_floor)
            return True
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{filename}'. Check file format.")
            return False
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False