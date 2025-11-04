from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.i18n import set_language  # jeśli gdzieś używasz
from django.views.static import serve as static_serve

# === STATIC FRONTEND SETUP ===
FRONTEND_ROOT = (settings.BASE_DIR / 'static' / 'frontend').resolve()
ASSET_EXTS = r'(?:css|js|png|jpg|jpeg|gif|svg|webp|ico|ttf|woff|woff2|map)'

# pliki frontendowe w znanych podkatalogach
urlpatterns = [
    re_path(
        rf'^(?P<path>(admin|common|goodbye|login|menu|registration|welcome)/.*\.{ASSET_EXTS})$',
        static_serve,
        {'document_root': FRONTEND_ROOT},
        name='frontend_assets_dirs'
    ),
    re_path(
        rf'^frontend/(?P<path>.*\.{ASSET_EXTS})$',
        static_serve,
        {'document_root': FRONTEND_ROOT},
        name='frontend_assets_prefixed'
    ),
    re_path(
        r'^favicon\.ico$',
        static_serve,
        {'document_root': FRONTEND_ROOT, 'path': 'favicon.ico'},
        name='favicon'
    ),
    re_path(
        r'^\.well-known/appspecific/com\.chrome\.devtools\.json$',
        lambda r: JsonResponse({}, status=200),
        name='chrome_devtools_json'
    ),
]

# static/media w DEV
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# === HELPERS ===
def serve_root_asset(request, filename: str):
    """
    Szuka pliku w kilku typowych katalogach frontendowych (np. /form.js, /main.css).
    """
    for sub in ('', 'welcome/', 'common/', 'registration/', 'login/', 'menu/', 'goodbye/'):
        p = (FRONTEND_ROOT / sub / filename).resolve()
        if p.is_file() and (p == FRONTEND_ROOT or FRONTEND_ROOT in p.parents):
            return FileResponse(open(p, 'rb'))
    raise Http404


def render_first(request, candidates):
    """
    Spróbuj wyrenderować z template'ów; jeśli brak – zwróć plik ze static/frontend.
    """
    for cand in candidates:
        if not cand or '..' in cand or cand.startswith('/'):
            continue
        try:
            get_template(cand)
            return render(request, cand)
        except Exception:
            continue

    for cand in candidates:
        p = (FRONTEND_ROOT / cand).resolve()
        if p.is_file() and (p == FRONTEND_ROOT or FRONTEND_ROOT in p.parents):
            return FileResponse(open(p, 'rb'))
    raise Http404


def default_candidates(raw: str):
    raw = (raw or '').strip('/')
    if raw == '':
        return ['welcome/index.html']
    if raw.endswith('.html') or raw.endswith('.htm'):
        return [raw]
    return [f'{raw}/index.html', f'{raw}.html']


# aliasy do plików w root'cie
urlpatterns += [
    re_path(
        rf'^(?P<filename>[^/]+\.{ASSET_EXTS})$',
        lambda r, filename: serve_root_asset(r, filename),
        name='alias_root_assets'
    ),
]


def serve_template(request, tpl_path: str = ''):
    key = (tpl_path or '').strip('/').replace(' ', '').lower()
    if key in {'index.html'}:
        return render_first(request, ['menu/index.html', 'menu/dashboard.html', 'welcome/index.html'])
    if key in {'reserve.html'}:
        return render_first(request, ['menu/reserve.html', 'reserve/index.html', 'reserve.html'])
    if key in {'cancel.html', 'menu/cancel.html'}:
        return render_first(request, ['menu/cancel.html', 'cancel/index.html', 'cancel.html'])
    if key in {'', 'home', 'welcome'}:
        return render_first(request, ['welcome/index.html', 'index.html'])
    if key in {'login', 'log-in', 'signin', 'sign-in', 'login/index.html'}:
        return render_first(request, [
            'login/index.html',
            'login.html',
            'registration/index.html',
            'registration/login.html',
            'welcome/login.html',
            'login/magic_link.html',
            'welcome/index.html'
        ])
    if key in {'register', 'registration', 'signup', 'sign-up', 'register/index.html', 'signup/index.html'}:
        return render_first(request, [
            'register/index.html',
            'register.html',
            'registration/index.html',
            'registration/register.html',
            'registration/signup.html',
            'signup/index.html',
            'signup.html',
            'welcome/register.html',
            'welcome/signup.html'
        ])
    if key in {'dashboard', 'panel', 'menu'}:
        # Always prefer the modern dashboard for all users if available
        try:
            get_template('dashboard/dashboard.html')
            return render(request, 'dashboard/dashboard.html')
        except Exception:
            pass
        return render_first(request, ['dashboard/index.html', 'dashboard.html', 'menu/dashboard.html', 'menu/index.html', 'welcome/index.html'])
    if key in {'reserve', 'reservation', 'book', 'booking'}:
        return render_first(request, ['reserve/index.html', 'reserve.html', 'menu/reserve.html'])
    if key in {'cancel', 'cancellation'}:
        return render_first(request, ['cancel/index.html', 'cancel.html', 'menu/cancel.html'])
    if key in {'goodbye', 'logout', 'logout_goodbye_white'}:
        return render_first(request, ['goodbye/logout_goodbye_white.html', 'goodbye/index.html', 'goodbye.html'])
    if key in {'thank_you_spaced_clean.html'}:
        return render_first(request, ['thank_you_spaced_clean.html', 'welcome/thank_you_spaced_clean.html'])
    if key in {'profile', 'accounts/profile'}:
        return render_first(request, ['account/profile.html', 'profile/index.html', 'profile.html'])
    # /floor/<n> → przekierowanie do menu z parametrem
    if key.startswith('floor/'):
        floor_num = key.replace('floor/', '')
        return redirect(f'/menu/?floor={floor_num}')
    return render_first(request, default_candidates(tpl_path))


# === MOBILE DASHBOARD ===
@ensure_csrf_cookie
def mobile_dashboard(request):
    return render_first(request, [
        'dashboard.html',
        'dashboard/index.html',
        'menu/dashboard.html',
        'welcome/index.html',
    ])


# === MAIN URLS (KOLEJNOŚĆ MA ZNACZENIE) ===
urlpatterns += [
    path('admin/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),

    # TEN WPIS MUSI BYĆ PRZED routerem API:
    path('api/mobile/dashboard/', mobile_dashboard, name='mobile_dashboard'),

    # router API
    path('api/', include('api.urls')),

    # jeśli to powoduje błędy (np. brak requests), ZAKOMENTUJ na chwilę:
    path('reservations/', include('reservations.urls')),

    # allauth
    path('accounts/login/', lambda request: redirect('/login'), name='account_login_redirect'),
    path('accounts/', include('allauth.urls')),

    # magic link
    path(
        'auth/magic-link/<str:token>/',
        lambda request, token: redirect(f'/api/auth/magic-link/{token}/'),
        name='magic_link_redirect',
    ),

    # fallback frontend
    path('', serve_template, name='home'),
    re_path(r'^(?P<tpl_path>.*)$', serve_template, name='any_page'),
]
