from src.view.ConsoleCoworkingApp import ConsoleCoworkingApp


def get_floor_seat_data(floor, number_of_seats):
    """
    Tą funkcją tworzymy listę rezerwacji miejsc na danym piętrze.
    """
    # Sprawdzenie czy numer piętra jest prawidłowy. Zwracanie listy zawierającej numer piętra i liczba miejsc
    if floor not in (4, 5, 6, 7):
        # Jeśli numer piętra nie zgadza się wyświetli bład i  stopujemy program.
        raise ValueError('Invalid floor number.  Please use 4, 5, 6, or 7.')

    # Tworzymy liste która reprezentuje miejsca.
    # Zaczynamy od miejsc dostępnych, więc lista zawiera numery miejsc i status rezerwacji = False
    seats = []

    for seat_number in range(1, number_of_seats + 1):  # pętla od 1 do numeru miejsca
        seats.append([seat_number, False])

    # Zwracamy terraZ listę która ma w sobienumer piętra i listę dostępnych miejsc
    return [floor, seats]



def create_all_floors_data():
    """
    Funkcja ta tworzy głowene informacje o wszytskich piętrach i ich miejscach

    Używa funkcji get_floor_seat_data żeby uzyskać dane dla każdego piętra
    Zwraca listę list gdzie każda wewnetrzna lista reprezentuje piętro i jego miejsca
    """
    # Zdefiniowanie numery pięter i liczbę miejsc na każdym piętrze
    floor_numbers = [4, 5, 6, 7]
    number_of_seats_per_floor = [20, 30, 25, 35]

    # Tworzymy pustą listę aby przechować dane dla wszystkich pięter
    all_floors_data = []

    # Pętla któa przechodzi przez każde piętro i miejsce
    for i in range(len(floor_numbers)):
        floor = floor_numbers[i]
        seats = number_of_seats_per_floor[i]
        #Pobranie info o miejscach na bieżącym piętrze
        floor_data = get_floor_seat_data(floor, seats)
        # Dodanie danych dla tego pietra do listy wszystkich pięter
        all_floors_data.append(floor_data)

    # Zwrócenie pełnej struktury danych
    return all_floors_data



def main_app():
    """
   Główna funkcja w której program działa w sensie np wywołuje inne funckje - można a nawet chyba trzeba to zrobić w osobnym Pliku - Michał się wypowie
    """
    # Struktura danych zawierajaca rezerwacje miejsc na wsyztskich piętrach
    all_seats_data = create_all_floors_data()

    # Wywołanie klasy ConsoleCoworkingApp z danymi o miejscach
    app = ConsoleCoworkingApp(all_seats_data)
    app.start()
    # Całą struktura w senise jej wydrukownaie
    # print("Pełna struktura :")
    # print(all_seats_data)
    #
    # # Informacje o miejscach dla każdego piętra
    # print("4th floor:")
    # print(all_seats_data[0])
    # print("5th floor:")
    # print(all_seats_data[1])
    # print("6th floor:")
    # print(all_seats_data[2])
    # print("7th floor:")
    # print(all_seats_data[3])


if __name__ == "__main__":
    main_app()