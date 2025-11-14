"""
Magic Link Authentication System
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.db import models

User = get_user_model()


class MagicLink(models.Model):
    """Model for storing magic links"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='magic_links')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"MagicLink for {self.user.email} - {'Used' if self.used else 'Active'}"
    
    def is_valid(self):
        """Check if magic link is valid and not expired"""
        return not self.used and timezone.now() < self.expires_at
    
    def use(self):
        """Mark magic link as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save()


class MagicLinkService:
    """Service for handling magic link operations"""
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(settings.MAGIC_LINK_LENGTH)
    
    @staticmethod
    def create_magic_link(user):
        """Create a new magic link for user"""
        # Clean up old unused links for this user
        MagicLink.objects.filter(user=user, used=False).delete()
        
        # Create new magic link
        token = MagicLinkService.generate_token()
        expires_at = timezone.now() + timedelta(seconds=settings.MAGIC_LINK_VALIDITY)
        
        magic_link = MagicLink.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return magic_link
    
    @staticmethod
    def send_magic_link_email(user, magic_link, request=None):
        """Send magic link email to user"""
        # Build the magic link URL
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = "http://127.0.0.1:8000"
        
        magic_url = f"{base_url}/auth/magic-link/{magic_link.token}/"
        
        validity_minutes = settings.MAGIC_LINK_VALIDITY // 60
        
        # Prepare context for templates
        context = {
            'user': user,
            'magic_url': magic_url,
            'validity_minutes': validity_minutes,
        }
        
        # Render subject from template
        subject = render_to_string('emails/magic_link_subject.txt', context).strip()
        
        # Render both plain text and HTML versions
        message_plain = render_to_string('emails/magic_link_body.txt', context)
        message_html = render_to_string('emails/magic_link_body.html', context)
        
        # Send email with both plain text and HTML
        from django.core.mail import EmailMultiAlternatives
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=message_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    @staticmethod
    def authenticate_with_token(token):
        """Authenticate user with magic link token"""
        try:
            magic_link = MagicLink.objects.get(token=token)
            
            if not magic_link.is_valid():
                return None
            
            # Mark as used
            magic_link.use()
            
            return magic_link.user
            
        except MagicLink.DoesNotExist:
            return None
    
    @staticmethod
    def cleanup_expired_links():
        """Clean up expired magic links"""
        expired_count = MagicLink.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        return expired_count
