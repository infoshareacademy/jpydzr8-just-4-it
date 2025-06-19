from src.model.coworking_model import Floor, Coworking, User
from src.view.console_coworking_app import ConsoleCoworkingApp


def main():
    floor_numbers = ((4, 20), (5, 30), (6, 25), (7, 35))
    floors = [Floor(floor_number, number_of_seats) for floor_number, number_of_seats in floor_numbers]
    john_doe = User("John", "Doe", "john@doe.com", "123456789")
    coworking = Coworking(floors,[john_doe])
    app = ConsoleCoworkingApp(coworking)
    # app.start()
    # floors[0].seats[0].reserved = True
    # floors[0].seats[10].reserved = True
    # floors[2].seats[0].reserved = True
    # floors[3].seats[0].reserved = True
    app.start()



if __name__ == "__main__":
    main()