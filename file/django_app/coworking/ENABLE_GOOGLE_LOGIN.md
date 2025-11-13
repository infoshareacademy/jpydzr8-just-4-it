# 🔧 Jak włączyć Google Login po konfiguracji

## ✅ **Status obecny:**
- Google Login jest **tymczasowo wyłączony** aby uniknąć błędów 400
- Wszystkie inne funkcje działają normalnie
- Email 2FA jest w pełni funkcjonalny

## 🚀 **Jak włączyć Google Login:**

### 1. **Skonfiguruj Google OAuth**
Postępuj zgodnie z instrukcjami w `GOOGLE_OAUTH_INSTRUCTIONS.md`:
- Utwórz projekt w Google Cloud Console
- Skonfiguruj OAuth 2.0 Client ID
- Zaktualizuj wartości w Django Admin

### 2. **Włącz przycisk Google Login**
Po skonfigurowaniu prawdziwych kluczy Google:

#### **W pliku `templates/login/index.html`:**
```html
<!-- Usuń komentarz z tej sekcji: -->
<div class="divider">
  <span>{% trans 'or' %}</span>
</div>

<div class="social-login">
  <a href="/accounts/google/login/" class="btn btn-google">
    <!-- SVG Google logo -->
    {% trans 'Continue with Google' %}
  </a>
</div>
```

#### **W pliku `templates/registration/index.html`:**
```html
<!-- Usuń komentarz z tej sekcji: -->
<div class="divider">
    <span>{% trans 'or' %}</span>
</div>

<div class="social-login">
    <a href="/accounts/google/login/" class="btn btn-google">
        <!-- SVG Google logo -->
        {% trans 'Continue with Google' %}
    </a>
</div>
```

### 3. **Testuj Google Login**
- Przejdź do http://127.0.0.1:8000/login
- Kliknij "Continue with Google"
- Sprawdź czy przekierowanie do Google działa

## 🎯 **Co działa teraz:**
- ✅ Standardowe logowanie/rejestracja
- ✅ Email 2FA (pełna funkcjonalność)
- ✅ Panel bezpieczeństwa `/security`
- ✅ API endpoints dla 2FA

## ⏳ **Co wymaga konfiguracji:**
- 🔧 Google OAuth (tymczasowo wyłączony)
- 📧 Prawdziwy SMTP dla emaili (obecnie console backend)

## 📋 **Szybka lista kontrolna:**
- [ ] Google Cloud Console projekt utworzony
- [ ] OAuth 2.0 Client ID skonfigurowany
- [ ] Redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`
- [ ] Client ID i Secret zaktualizowane w Django Admin
- [ ] Przyciski Google Login odkomentowane w szablonach
- [ ] Test Google Login wykonany

---

**Google Login jest gotowy do włączenia po konfiguracji prawdziwych kluczy!** 🚀



