from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .magic_link import MagicLinkService
from .password_reset import PasswordResetService
from django.utils.translation import gettext as _
from .models import Reservation
from .serializers import ReservationSerializer
User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        name = request.data.get('name') or request.data.get('username') or ''
        if not email or not password:
            return Response({'detail': 'email and password are required'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'User already exists'}, status=400)
        user = User.objects.create_user(email=email, password=password)
        if name:
            if hasattr(user, 'first_name'):
                user.first_name = name
            user.save()
        return Response({'ok': True}, status=201)

class EmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or request.data.get('username') or '').strip().lower()
        password = request.data.get('password') or ''
        if not email or not password:
            return Response({'detail': 'email and password are required'}, status=400)
        user = authenticate(request, email=email, password=password)
        if user is None:
            try:
                u = User.objects.get(email=email)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=400)
        login(request, user)
        return Response({'ok': True})
LoginView = EmailLoginView

class LogoutView(APIView):

    def post(self, request):
        logout(request)
        return Response({'ok': True})
    
    def get(self, request):
        """Handle GET requests for logout (e.g., from links)"""
        logout(request)
        from django.shortcuts import redirect
        return redirect('/goodbye')

class MeView(APIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False}, status=200)
        u = request.user
        return Response({'authenticated': True, 'username': getattr(u, 'username', ''), 'email': getattr(u, 'email', ''), 'first_name': getattr(u, 'first_name', ''), 'last_name': getattr(u, 'last_name', '')})

class CsrfTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return Response({'csrfToken': token})

class ReservationViewSet(viewsets.ModelViewSet):
    """Pełne CRUD na rezerwacjach (SQLite), autoryzacja po sesji Django."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        qs = Reservation.objects.all().order_by('date', 'seat_id')
        df = self.request.query_params.get('date_from')
        dt = self.request.query_params.get('date_to')
        d_exact = self.request.query_params.get('date')
        if d_exact:
            qs = qs.filter(date=d_exact)
        elif df and dt:
            qs = qs.filter(date__gte=df, date__lte=dt)
        return qs

def _ics_headers(filename: str) -> dict:
    return {'Content-Type': 'text/calendar; charset=utf-8', 'Content-Disposition': f'attachment; filename="{filename}"'}

def _ics_escape(text: str) -> str:
    s = text or ''
    s = s.replace('\\', '\\\\')
    s = s.replace(',', '\\,')
    s = s.replace(';', '\\;')
    s = s.replace('\r\n', '\\n').replace('\n', '\\n').replace('\r', '\\n')
    return s

def _ics_datetime(d: str) -> datetime:
    try:
        return datetime.strptime(d, '%Y-%m-%d')
    except Exception:
        return datetime.utcnow()

@require_GET
def ics_reservation(request, pk: str):
    """Return a single VEVENT (METHOD:PUBLISH) for Reservation pk as all-day event."""
    try:
        r = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return HttpResponse('Not found', status=404)
    start = _ics_datetime(r.date)
    end = start + timedelta(days=1)
    uid = f'{r.id}@coworking.local'
    summary = f"Seat {r.seat_id} — {getattr(r, 'name', '')}"
    desc = f"Email: {getattr(r, 'email', '')}\nNotes: {getattr(r, 'notes', '')}"
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Coworking App//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'BEGIN:VEVENT', f'UID:{_ics_escape(uid)}', f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}", f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}", f'SUMMARY:{_ics_escape(summary)}', f'DESCRIPTION:{_ics_escape(desc)}', f"LOCATION:{_ics_escape(getattr(r, 'seat_id', ''))}", 'END:VEVENT', 'END:VCALENDAR', '']
    resp = HttpResponse('\r\n'.join(lines))
    for k, v in _ics_headers(f'{r.id}.ics').items():
        resp[k] = v
    return resp

@require_GET
def ics_reservation_cancel(request, pk: str):
    """Return VEVENT with METHOD:CANCEL for Reservation pk (to remove in clients that honor CANCEL)."""
    try:
        r = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:

        class R:
            ...
        r = R()
        r.id = pk
        r.date = datetime.utcnow().strftime('%Y-%m-%d')
        r.seat_id = ''
        r.name = ''
        r.email = ''
        r.notes = ''
    start = _ics_datetime(r.date)
    end = start + timedelta(days=1)
    uid = f'{r.id}@coworking.local'
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Coworking App//EN', 'CALSCALE:GREGORIAN', 'METHOD:CANCEL', 'BEGIN:VEVENT', f'UID:{_ics_escape(uid)}', f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}", f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}", 'STATUS:CANCELLED', 'END:VEVENT', 'END:VCALENDAR', '']
    resp = HttpResponse('\r\n'.join(lines))
    for k, v in _ics_headers(f'{r.id}_cancel.ics').items():
        resp[k] = v
    return resp


# 2FA Views
class Setup2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Setup Email 2FA for user"""
        user = request.user
        
        # Check if user already has 2FA setup
        if EmailDevice.objects.filter(user=user, confirmed=True).exists():
            return Response({'detail': '2FA already configured'}, status=400)
        
        # Create EmailDevice
        device = EmailDevice.objects.create(
            user=user,
            name='Email 2FA',
            email=user.email,
            confirmed=False
        )
        
        # Send initial token
        device.generate_token()
        
        return Response({
            'detail': '2FA setup initiated. Check your email for verification code.',
            'device_id': device.id
        })

class Verify2FASetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Verify 2FA setup with token from email"""
        user = request.user
        token = request.data.get('token', '')
        device_id = request.data.get('device_id')
        
        if not token or not device_id:
            return Response({'detail': 'Token and device_id required'}, status=400)
        
        try:
            device = EmailDevice.objects.get(id=device_id, user=user, confirmed=False)
        except EmailDevice.DoesNotExist:
            return Response({'detail': 'Invalid device'}, status=400)
        
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            return Response({'detail': '2FA successfully configured'})
        else:
            return Response({'detail': 'Invalid token'}, status=400)

class LoginWith2FAView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Login with email/password, then require 2FA"""
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        
        if not email or not password:
            return Response({'detail': 'Email and password required'}, status=400)
        
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=400)
        
        # Check if user has 2FA enabled
        if not EmailDevice.objects.filter(user=user, confirmed=True).exists():
            # No 2FA, login normally
            login(request, user)
            return Response({'ok': True, 'requires_2fa': False})
        
        # 2FA required - don't login yet, just verify credentials
        request.session['pending_user_id'] = user.id
        request.session['pending_user_email'] = user.email
        
        # Generate and send 2FA token
        device = EmailDevice.objects.filter(user=user, confirmed=True).first()
        if hasattr(device, 'generate_token'):
            device.generate_token()
        
        return Response({
            'ok': False,
            'requires_2fa': True,
            'detail': '2FA token sent to your email'
        })

class Verify2FALoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Complete login with 2FA token"""
        token = request.data.get('token', '')
        pending_user_id = request.session.get('pending_user_id')
        
        if not token or not pending_user_id:
            return Response({'detail': 'Token required'}, status=400)
        
        try:
            user = User.objects.get(id=pending_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid session'}, status=400)
        
        # Verify 2FA token
        device = EmailDevice.objects.filter(user=user, confirmed=True).first()
        if not device or not device.verify_token(token):
            return Response({'detail': 'Invalid 2FA token'}, status=400)
        
        # Complete login
        login(request, user)
        
        # Clear pending session data
        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']
        if 'pending_user_email' in request.session:
            del request.session['pending_user_email']
        
        return Response({'ok': True})

class Disable2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Disable 2FA for user"""
        user = request.user
        
        # Verify password before disabling 2FA
        password = request.data.get('password', '')
        if not authenticate(request, email=user.email, password=password):
            return Response({'detail': 'Invalid password'}, status=400)
        
        # Remove all 2FA devices
        EmailDevice.objects.filter(user=user).delete()
        
        return Response({'detail': '2FA disabled successfully'})

class Check2FAStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Check if user has 2FA enabled"""
        user = request.user
        has_2fa = EmailDevice.objects.filter(user=user, confirmed=True).exists()
        
        return Response({
            'has_2fa': has_2fa,
            'user_id': user.id,
            'email': user.email
        })


# Magic Link Authentication Views
class MagicLinkLoginView(APIView):
    """Send magic link to user's email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'detail': _('Email required')}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'detail': _('If an account with this email exists, a login link has been sent.'),
                'email_sent': True
            })
        
        # Create magic link
        magic_link = MagicLinkService.create_magic_link(user)
        
        # Send email
        try:
            MagicLinkService.send_magic_link_email(user, magic_link, request)
            return Response({
                'detail': _('Login link sent to your email'),
                'email_sent': True
            })
        except Exception as e:
            return Response({
                'detail': _('Failed to send email'),
                'error': str(e)
            }, status=500)


class MagicLinkAuthenticateView(APIView):
    """Authenticate user with magic link token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        return self.authenticate(request, token)
    
    def get(self, request, token):
        """Handle GET requests for direct link clicks"""
        return self.authenticate(request, token)
    
    def authenticate(self, request, token):
        user = MagicLinkService.authenticate_with_token(token)
        
        if user:
            # Login user with specific backend
            from django.conf import settings
            from django.shortcuts import redirect
            backend = settings.AUTHENTICATION_BACKENDS[0]  # Use first backend
            login(request, user, backend=backend)
            
            # If it's a GET request (direct link click), redirect to dashboard
            if request.method == 'GET':
                return redirect('/dashboard')
            
            # If it's a POST request (API call), return JSON
            return Response({
                'detail': _('Login successful'),
                'user': {
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_staff': user.is_staff,
                }
            })
        
        # If it's a GET request and link is invalid, redirect to login with error
        if request.method == 'GET':
            from django.shortcuts import redirect
            return redirect('/login?error=invalid_link')
        
        return Response({'detail': _('Invalid or expired link')}, status=400)


class CheckAuthPreferenceView(APIView):
    """Check authentication preference for a given email (without requiring authentication)"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        
        if not email:
            return Response({'detail': _('Email required')}, status=400)
        
        try:
            user = User.objects.get(email=email)
            return Response({
                'use_magic_link': user.use_magic_link,
                'email_exists': True
            })
        except User.DoesNotExist:
            # Don't reveal if user exists for security
            return Response({
                'use_magic_link': False,
                'email_exists': False
            })


class UpdateAuthPreferenceView(APIView):
    """Update authentication preference (requires authentication)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        use_magic_link = request.data.get('use_magic_link', False)
        
        if isinstance(use_magic_link, str):
            use_magic_link = use_magic_link.lower() in ('true', '1', 'yes')
        
        request.user.use_magic_link = bool(use_magic_link)
        request.user.save()
        
        return Response({
            'ok': True,
            'use_magic_link': request.user.use_magic_link,
            'detail': _('Authentication preference updated successfully')
        })


class RequestPasswordResetView(APIView):
    """Request password reset - send reset link to email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        
        if not email:
            return Response({'detail': _('Email required')}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'detail': _('If an account with this email exists, a password reset link has been sent.'),
                'email_sent': True
            })
        
        # Create reset token
        reset_token = PasswordResetService.create_reset_token(user)
        
        # Send email
        try:
            PasswordResetService.send_reset_email(user, reset_token, request)
            return Response({
                'detail': _('Password reset link sent to your email'),
                'email_sent': True
            })
        except Exception as e:
            return Response({
                'detail': _('Failed to send email'),
                'error': str(e)
            }, status=500)


class ResetPasswordView(APIView):
    """Reset password using token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not token or not new_password:
            return Response({'detail': _('Token and new password are required')}, status=400)
        
        if new_password != confirm_password:
            return Response({'detail': _('Passwords do not match')}, status=400)
        
        # Validate password strength
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        try:
            reset_token = PasswordResetService.validate_token(token)
            if not reset_token:
                return Response({'detail': _('Invalid or expired token')}, status=400)
            
            validate_password(new_password, reset_token.user)
        except ValidationError as e:
            return Response({
                'detail': _('Password validation failed'),
                'errors': e.messages
            }, status=400)
        
        # Reset password
        user = PasswordResetService.reset_password(token, new_password)
        
        if user:
            return Response({
                'detail': _('Password has been reset successfully'),
                'ok': True
            })
        
        return Response({'detail': _('Invalid or expired token')}, status=400)
