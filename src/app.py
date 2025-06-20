from src.model.coworking_model import Floor, Coworking
from src.view.console_coworking_app import ConsoleCoworkingApp


def main():
    coworking = Coworking.load_from_json()
    if coworking is None:
        floor_numbers = ((4, 20), (5, 30), (6, 25), (7, 35))
        floors = [Floor(floor_number, number_of_seats) for floor_number, number_of_seats in floor_numbers]
        coworking = Coworking(floors)
        coworking.save_to_json()

    app = ConsoleCoworkingApp(coworking)
    app.start()


if __name__ == "__main__":
    main()