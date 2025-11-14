# Jak wrzucić projekt na Git - Instrukcja dla kolegów

## Krok 1: Skopiuj folder z pendrive
Skopiuj cały folder `django_app` z pendrive na swój komputer.

## Krok 2: Przejdź do folderu projektu
```bash
cd django_app
```

## Krok 3: Zainicjalizuj repozytorium Git (jeśli jeszcze nie ma)
```bash
git init
```

## Krok 4: Stwórz nowy branch
```bash
git checkout -b moj-branch
# lub
git checkout -b dev
# lub jakikolwiek inny branch
```

## Krok 5: Dodaj wszystkie pliki
```bash
git add .
```

## Krok 6: Sprawdź co zostanie dodane (opcjonalnie)
```bash
git status
```

## Krok 7: Zrób commit
```bash
git commit -m "Initial commit - projekt coworking z rezerwacjami i użytkownikami"
```

## Krok 8: Dodaj remote (jeśli masz już repo na GitHub/GitLab)
```bash
git remote add origin https://github.com/twoj-username/nazwa-repo.git
# lub
git remote add origin git@github.com:twoj-username/nazwa-repo.git
```

## Krok 9: Wypchnij na remote
```bash
git push -u origin moj-branch
# lub nazwa twojego brancha
```

---

## Jeśli chcesz stworzyć nowe repo na GitHub:

1. Wejdź na https://github.com
2. Kliknij "New repository"
3. Nadaj nazwę (np. `coworking-app`)
4. **NIE** zaznaczaj "Initialize with README" (bo już mamy pliki)
5. Kliknij "Create repository"
6. Skopiuj URL repo (HTTPS lub SSH)
7. Wykonaj kroki 8-9 powyżej

---

## Ważne informacje:

- ✅ Baza danych `db.sqlite3` jest włączona do repo - koledzy zobaczą Twoje rezerwacje i użytkowników
- ✅ Plik `.env` jest wykluczony (bezpieczeństwo) - każdy musi stworzyć swój własny z `env_example.txt`
- ✅ Folder `venv/` jest wykluczony - każdy musi stworzyć własne środowisko wirtualne
- ✅ Wszystkie logi i pliki tymczasowe są wykluczone

---

## Po wrzuceniu na repo - dla kolegów:

Koledzy mogą pobrać projekt:
```bash
git clone https://github.com/twoj-username/nazwa-repo.git
cd nazwa-repo
git checkout moj-branch  # lub nazwa brancha
```

Następnie postępują zgodnie z instrukcjami w `coworking/README.md`

