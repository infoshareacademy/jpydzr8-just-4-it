from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render, redirect
from django.http import Http404, FileResponse, JsonResponse
from django.template.loader import get_template
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.views.i18n import set_language
from pathlib import Path
FRONTEND_ROOT = (settings.BASE_DIR / 'static' / 'frontend').resolve()
ASSET_EXTS = '(?:css|js|png|jpg|jpeg|gif|svg|webp|ico|ttf|woff|woff2|map)'
urlpatterns = [re_path(f'^(?P<path>(admin|common|goodbye|login|menu|registration|welcome)/.*\\.{ASSET_EXTS})$', static_serve, {'document_root': FRONTEND_ROOT}, name='frontend_assets_dirs'), re_path(f'^frontend/(?P<path>.*\\.{ASSET_EXTS})$', static_serve, {'document_root': FRONTEND_ROOT}, name='frontend_assets_prefixed'), re_path('^favicon\\.ico$', static_serve, {'document_root': FRONTEND_ROOT, 'path': 'favicon.ico'}, name='favicon'), re_path('^\\.well-known/appspecific/com\\.chrome\\.devtools\\.json$', lambda r: JsonResponse({}, status=200), name='chrome_devtools_json')]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def serve_root_asset(request, filename: str):
    """
    Spróbuj znaleźć plik w kilku typowych katalogach frontendowych.
    Obsługuje np. /form.js, /main.css, /logo.png ...
    """
    for sub in ('', 'welcome/', 'common/', 'registration/', 'login/', 'menu/', 'goodbye/'):
        p = (FRONTEND_ROOT / sub / filename).resolve()
        if p.is_file() and (p == FRONTEND_ROOT or FRONTEND_ROOT in p.parents):
            return FileResponse(open(p, 'rb'))
    raise Http404

def render_first(request, candidates):
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
urlpatterns += [re_path(f'^(?P<filename>[^/]+\\.{ASSET_EXTS})$', lambda r, filename: serve_root_asset(r, filename), name='alias_root_assets')]

def serve_template(request, tpl_path: str=''):
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
        return render_first(request, ['login/magic_link.html', 'login/index.html', 'login.html', 'registration/index.html', 'registration/login.html', 'welcome/login.html', 'welcome/index.html'])
    if key in {'register', 'registration', 'signup', 'sign-up', 'register/index.html', 'signup/index.html'}:
        return render_first(request, ['register/index.html', 'register.html', 'registration/index.html', 'registration/register.html', 'registration/signup.html', 'signup/index.html', 'signup.html', 'welcome/register.html', 'welcome/signup.html'])
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
    # Handle floor URLs - redirect to menu with floor parameter
    if key.startswith('floor/'):
        floor_num = key.replace('floor/', '')
        # Redirect to menu with floor parameter for automatic scrolling
        return redirect(f'/menu/?floor={floor_num}')
    return render_first(request, default_candidates(tpl_path))
urlpatterns += [
    path('admin/', admin.site.urls), 
    path('api/', include('api.urls')), 
    path('reservations/', include('reservations.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    # Przekieruj accounts/login na nasz formularz z 2FA
    path('accounts/login/', lambda request: redirect('/login'), name='account_login_redirect'),
    path('accounts/', include('allauth.urls')),
    # Magic link redirect for convenience
    path('auth/magic-link/<str:token>/', lambda request, token: redirect(f'/api/auth/magic-link/{token}/'), name='magic_link_redirect'),
    path('', serve_template, name='home'), 
    re_path('^(?P<tpl_path>.*)$', serve_template, name='any_page')
]
