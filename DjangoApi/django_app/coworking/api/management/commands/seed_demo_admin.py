from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create/update a demo superuser"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = "demo@acme.io"
        pwd = "Demo123!"
        u, created = User.objects.get_or_create(email=email, defaults={"is_staff": True, "is_superuser": True})
        if not created:
            u.is_staff = True
            u.is_superuser = True
        u.set_password(pwd)
        u.save()
        self.stdout.write(self.style.SUCCESS(f"Superuser ready: {email} / {pwd}"))
