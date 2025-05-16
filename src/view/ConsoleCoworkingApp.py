import sys
from typing import List, Tuple

# Consolowe przedstawienie aplikacji.
class ConsoleCoworkingApp:
    def __init__(self, data: Tuple[int, List[Tuple[int, bool]]]):
        self.data = data

    def print_menu(self):
        """
        Tą funkcją wyświetlamy menu w konsoli.
        """
        print("1. Pokaż dostępne miejsca")
        print("2. Rezerwuj miejsce")
        print("3. Anuluj rezerwację")
        print("4. Wyjdź")

    def handle_menu_option(self, option):
        """
        Tą funkcją obsługujemy wybraną opcję z menu.
        """
        if option == "1":
            self.print_data()
        elif option == "2":
            print("Rezerwuj miejsce...")
        elif option == "3":
            print("Anuluj rezerwację...")
        elif option == "4":
            print("Wyjdź.")
            sys.exit(0)
        else:
            print("Niepoprawny wybór. Proszę spróbować ponownie.")

    def print_data(self):
        """
        Tą funkcją wyświetlamy dostępne miejsca na każdym piętrze.
        """
        for floor, seats in self.data:
            print(f"Piętro {floor}:" , end=" ")
            for seat, reserved in seats:
                print(f"{seat}({'X' if reserved else 'O'})" , end=" ")
            print("")

    def start(self):
        """
        Tą funkcją uruchamiamy aplikację.
        """
        print("Witaj w aplikacji do rezerwacji miejsc!")
        while True:
            self.print_menu()
            selected_option = input("Wybierz opcję (1-4): ")
            self.handle_menu_option(selected_option)
            is_continue = input("Czy chcesz kontynuować? (t/n): ")
            if is_continue.strip().lower() != "t":
                break

if __name__ == "__main__":
    app = ConsoleCoworkingApp([])
    app.start()