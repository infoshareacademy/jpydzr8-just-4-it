"""
Password Reset System
"""
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.db import models

User = get_user_model()

# Import this model in api/models.py or api/__init__.py to make it discoverable by Django
__all__ = ['PasswordResetToken', 'PasswordResetService']


class PasswordResetToken(models.Model):
    """Model for storing password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PasswordResetToken for {self.user.email} - {'Used' if self.used else 'Active'}"
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.used and timezone.now() < self.expires_at
    
    def use(self):
        """Mark token as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save()


class PasswordResetService:
    """Service for handling password reset operations"""
    
    # Token validity: 1 hour
    TOKEN_VALIDITY = 3600  # seconds
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_reset_token(user):
        """Create a new password reset token for user"""
        # Clean up old unused tokens for this user
        PasswordResetToken.objects.filter(user=user, used=False).delete()
        
        # Create new token
        token = PasswordResetService.generate_token()
        expires_at = timezone.now() + timedelta(seconds=PasswordResetService.TOKEN_VALIDITY)
        
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return reset_token
    
    @staticmethod
    def send_reset_email(user, reset_token, request=None):
        """Send password reset email to user"""
        # Build the reset URL
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = "http://127.0.0.1:8000"
        
        reset_url = f"{base_url}/reset-password/{reset_token.token}/"
        
        validity_minutes = PasswordResetService.TOKEN_VALIDITY // 60
        
        # Prepare context for templates
        context = {
            'user': user,
            'reset_url': reset_url,
            'validity_minutes': validity_minutes,
            'token': reset_token.token,
        }
        
        # Render subject
        subject = _('Password Reset Request - Just 4 IT Coworking')
        
        # Render message
        message = _(
            'Hello %(name)s,\n\n'
            'You requested a password reset for your account.\n\n'
            'Click the link below to reset your password:\n'
            '%(url)s\n\n'
            'This link will expire in %(minutes)d minutes.\n\n'
            'If you did not request this, please ignore this email.\n\n'
            'Best regards,\n'
            'Just 4 IT Coworking Team'
        ) % {
            'name': user.full_name or user.email,
            'url': reset_url,
            'minutes': validity_minutes
        }
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return True
    
    @staticmethod
    def validate_token(token):
        """Validate password reset token"""
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return None
            
            return reset_token
            
        except PasswordResetToken.DoesNotExist:
            return None
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset user password using token"""
        reset_token = PasswordResetService.validate_token(token)
        
        if not reset_token:
            return None
        
        # Set new password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.use()
        
        return user
    
    @staticmethod
    def cleanup_expired_tokens():
        """Clean up expired password reset tokens"""
        expired_count = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        return expired_count


