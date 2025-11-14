# 🚀 Instrukcje konfiguracji Google OAuth

## ✅ **Co zostało zrobione:**
- Google OAuth jest skonfigurowany z placeholder wartościami
- Przycisk "Continue with Google" jest widoczny na stronach logowania i rejestracji
- Django Admin jest gotowy do konfiguracji

## 🔧 **Aby Google Login działał, wykonaj te kroki:**

### 1. **Przejdź do Google Cloud Console**
👉 https://console.cloud.google.com/

### 2. **Utwórz projekt (lub wybierz istniejący)**
- Kliknij "New Project"
- Wpisz nazwę: "Coworking App"
- Kliknij "Create"

### 3. **Włącz Google+ API**
- W menu po lewej: "APIs & Services" > "Library"
- Wyszukaj "Google+ API"
- Kliknij "Enable"

### 4. **Utwórz OAuth 2.0 Client ID**
- Przejdź do "APIs & Services" > "Credentials"
- Kliknij "Create Credentials" > "OAuth 2.0 Client ID"
- Wybierz "Web application"
- Wpisz nazwę: "Coworking App OAuth"
- W "Authorized redirect URIs" dodaj:
  ```
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```
- Kliknij "Create"

### 5. **Skopiuj Client ID i Client Secret**
- Po utworzeniu zobaczysz okno z danymi
- Skopiuj **Client ID** i **Client Secret**

### 6. **Zaktualizuj konfigurację w Django Admin**
👉 Przejdź do: http://127.0.0.1:8000/admin/socialaccount/socialapp/

- Kliknij na "Google" (lub utwórz nowy jeśli nie istnieje)
- Wpisz:
  - **Name**: `Google`
  - **Provider**: `Google`
  - **Client id**: `[Twój Client ID z Google]`
  - **Secret key**: `[Twój Client Secret z Google]`
  - **Sites**: Wybierz `127.0.0.1:8000`
- Kliknij "Save"

### 7. **Przetestuj Google Login**
- Przejdź do: http://127.0.0.1:8000/login
- Kliknij "Continue with Google"
- Powinieneś zostać przekierowany do Google

## 🔍 **Dostęp do Django Admin:**
- **URL**: http://127.0.0.1:8000/admin
- **Login**: `admin@example.com`
- **Hasło**: (nie ustawione)

### Aby ustawić hasło dla admin:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(email='admin@example.com')
>>> admin.set_password('twoje_haslo')
>>> admin.save()
```

## 🎯 **Co teraz działa:**
- ✅ Przycisk Google Login jest widoczny
- ✅ Strona nie pokazuje błędu 500
- ✅ Gotowe do konfiguracji prawdziwych kluczy

## ⚠️ **Obecny stan:**
- Przycisk Google Login przekieruje do Google
- Ale Google pokaże błąd "Invalid client"
- To normalne - dopóki nie skonfigurujesz prawdziwych kluczy

## 🎉 **Po konfiguracji:**
- Użytkownicy będą mogli logować się przez Google
- Automatyczne tworzenie kont użytkowników
- Dostęp do profilu Google (email, imię, zdjęcie)

---

**Gotowe! Teraz możesz skonfigurować prawdziwe klucze Google OAuth.** 🚀



