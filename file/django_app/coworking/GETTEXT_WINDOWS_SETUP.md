# Instalacja GNU gettext na Windows

## Problem

Podczas uruchamiania komendy `python manage.py compilemessages` na Windows możesz otrzymać błąd:

```
CommandError: Can't find msgfmt. Make sure you have GNU gettext tools 0.19 or newer installed.
```

Dzieje się tak, ponieważ Django potrzebuje narzędzi GNU gettext do kompilacji plików tłumaczeń (`.po` → `.mo`), a na Windows nie są one domyślnie zainstalowane.

## Rozwiązanie

### Opcja 1: Instalacja przez Chocolatey (Zalecane)

1. **Zainstaluj Chocolatey** (jeśli jeszcze nie masz):
   - Otwórz PowerShell jako Administrator
   - Uruchom:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```

2. **Zainstaluj gettext**:
   ```powershell
   choco install gettext
   ```

3. **Dodaj do PATH** (jeśli nie zostało dodane automatycznie):
   - Sprawdź czy `C:\ProgramData\chocolatey\lib\gettext\tools\bin` jest w PATH
   - Jeśli nie, dodaj ręcznie w ustawieniach systemowych

4. **Zweryfikuj instalację**:
   ```powershell
   msgfmt --version
   ```

5. **Uruchom ponownie kompilację**:
   ```bash
   python manage.py compilemessages
   ```

### Opcja 2: Instalacja ręczna

1. **Pobierz gettext dla Windows**:
   - Pobierz z: https://mlocati.github.io/articles/gettext-iconv-windows.html
   - Lub użyj bezpośredniego linku: https://github.com/mlocati/gettext-iconv-windows/releases

2. **Rozpakuj archiwum** (np. do `C:\gettext`)

3. **Dodaj do PATH**:
   - Otwórz "Zmienne środowiskowe" w Windows
   - Dodaj `C:\gettext\bin` do zmiennej PATH
   - Uruchom ponownie terminal

4. **Zweryfikuj instalację**:
   ```powershell
   msgfmt --version
   ```

5. **Uruchom ponownie kompilację**:
   ```bash
   python manage.py compilemessages
   ```

### Opcja 3: Użycie gotowych plików .mo (Tymczasowe rozwiązanie)

Jeśli nie możesz zainstalować gettext, możesz użyć już skompilowanych plików `.mo` z repozytorium:

1. Pliki `.mo` są już w repozytorium w folderze `locale/`
2. Jeśli są aktualne, możesz pominąć kompilację
3. **UWAGA**: Jeśli pliki `.po` zostały zaktualizowane, pliki `.mo` również muszą być zaktualizowane

## Weryfikacja

Po instalacji sprawdź czy wszystko działa:

```bash
# Sprawdź wersję gettext
msgfmt --version

# Skompiluj tłumaczenia
python manage.py compilemessages

# Sprawdź czy pliki .mo zostały zaktualizowane
python manage.py compilemessages -v 2
```

## Dodatkowe informacje

- **msgfmt** to narzędzie do kompilacji plików `.po` do `.mo`
- Pliki `.mo` są binarną wersją tłumaczeń używanych przez Django w runtime
- Po każdej zmianie w plikach `.po` należy uruchomić `compilemessages`

## Problemy?

Jeśli nadal masz problemy:

1. **Sprawdź PATH**: Upewnij się, że folder z `msgfmt.exe` jest w PATH
2. **Restart terminala**: Po zmianie PATH zamknij i otwórz terminal ponownie
3. **Sprawdź wersję**: `msgfmt --version` powinno pokazać wersję 0.19 lub nowszą
4. **Alternatywnie**: Użyj WSL (Windows Subsystem for Linux) i zainstaluj gettext w środowisku Linux

