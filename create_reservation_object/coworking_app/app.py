from models.coworking_model import Coworking, Floor, Seat
from controllers.coworking_controller import CoworkingController
from console_cooworking_app import ConsoleCoworkingApp

if __name__ == "__main__":
    coworking_space = Coworking()

    controller = CoworkingController(coworking_space)
    app = ConsoleCoworkingApp(controller)
    app.start()