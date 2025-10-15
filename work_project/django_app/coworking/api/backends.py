"""
Custom authentication backends
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to get email from kwargs or username parameter
        email = kwargs.get('email', username)
        
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        is_active field are allowed.
        """
        return getattr(user, 'is_active', True)



