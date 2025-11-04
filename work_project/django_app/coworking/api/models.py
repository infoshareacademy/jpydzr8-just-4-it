from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, full_name='', **extra):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, is_active=True, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, full_name='', **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, full_name=full_name, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    avatar = models.CharField(max_length=10, blank=True, default='👤', help_text='Avatar emoji or short identifier')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

class Reservation(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    seat_id = models.CharField(max_length=64, db_index=True)
    date = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    notes = models.CharField(max_length=1024, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['seat_id', 'date'], name='uq_resv_seat_date')]
