# Planowane rzeczy

Chcę dorobić w projekcie trzy konkretne tematy. Spisuję je tutaj, żeby było jasne, co jest do zrobienia i dlaczego.

## 1. Lista oczekujących
- **Cel:** użytkownicy powinni móc zapisać się na miejsce, które jest chwilowo zajęte, i dostać info, gdy się zwolni.
- **Do zrobienia:**
  - Uporządkować istniejący model `Waitlist` (sprawdzić, czy spełnia potrzeby).
  - Dodać widok/formularz w panelu, żeby łatwo się zapisać i wypisać.
  - Wysyłać mail/push, kiedy miejsce się zwolni (hook na zwolnienie rezerwacji).

## 2. Dostęp z zewnątrz
- **Cel:** umożliwić dostęp do wybranych funkcji (np. kalendarz dostępności, lista sal) dla użytkowników spoza firmy.
- **Do zrobienia:**
  - Przygotować bezpieczne endpointy publiczne (lub tokeny).
  - Zabezpieczyć dane wrażliwe – pokazywać tylko to, co można udostępnić.
  - Dorobić prosty frontend lub dokumentację, jak z tego korzystać.

## 3. Twarde ograniczenie rezerwacji tylko na mój użytkownik
- **Cel:** kiedy loguję się swoim kontem, nie chcę widzieć ani móc używać innych profili użytkowników.
- **Do zrobienia:**
  - W backendzie przyciąć API tak, żeby po zalogowaniu moim kontem (`email: ...`) widzieć i modyfikować tylko własne rezerwacje.
  - Ukryć w UI listę innych użytkowników, formularze zmiany kont itp.
  - Upewnić się, że w adminie też jest blokada (lub ograniczenie) dla tego konta.

## 3. Dwa loggery w aplikacji
- **Cel:** mieć porządny logging w kluczowych miejscach, żeby łatwo diagnozować problemy.
- **Do zrobienia:**
  - Dodać logger do mechanizmu listy oczekujących (zapisy, powiadomienia, błędy SMTP/push).
  - Dodać logger do integracji z zewnętrznym dostępem (wejścia/wyjścia API, błędy autoryzacji).
  - Skonfigurować format logów i poziomy w `settings.py`, tak żeby szły do osobnego pliku.

Tę listę będę aktualizował, kiedy pojawią się kolejne pomysły albo gdy któryś temat zamknę. Na razie – to są priorytety.

