""""
Custom authentication backends
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Allow logging in with email + password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # email może przyjść jako username (standard) lub w kwargs
        email = kwargs.get('email') or username
        if not email or not password:
            return None

        # normalizacja i case-insensitive lookup
        email = email.strip()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        # odrzuć nieaktywne konta, jeżeli pole istnieje
        return getattr(user, "is_active", True)
