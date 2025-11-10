"""
Management command to automatically setup email configuration
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Setup email configuration in .env file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for SMTP (e.g., your_email@gmail.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='App password for SMTP (for Gmail, get from https://myaccount.google.com/apppasswords)',
        )
        parser.add_argument(
            '--host',
            type=str,
            default='smtp.gmail.com',
            help='SMTP host (default: smtp.gmail.com)',
        )
        parser.add_argument(
            '--port',
            type=int,
            default=587,
            help='SMTP port (default: 587)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')
        host = options.get('host')
        port = options.get('port')
        
        base_dir = Path(settings.BASE_DIR)
        env_path = base_dir / '.env'
        
        if not email or not password:
            self.stdout.write(self.style.ERROR('❌ Email and password are required!'))
            self.stdout.write(self.style.WARNING('\nUsage:'))
            self.stdout.write('  python manage.py setup_email --email your_email@gmail.com --password your_app_password')
            self.stdout.write('\nFor Gmail:')
            self.stdout.write('  1. Go to: https://myaccount.google.com/apppasswords')
            self.stdout.write('  2. Create an App Password')
            self.stdout.write('  3. Use it as --password argument')
            return
        
        # Read existing .env or create new
        env_content = ''
        if env_path.exists():
            env_content = env_path.read_text()
        
        # Update or add email configuration
        lines = env_content.split('\n')
        updated_lines = []
        email_config_found = False
        
        for line in lines:
            if line.startswith('EMAIL_HOST='):
                updated_lines.append(f'EMAIL_HOST={host}')
                email_config_found = True
            elif line.startswith('EMAIL_PORT='):
                updated_lines.append(f'EMAIL_PORT={port}')
            elif line.startswith('EMAIL_USE_TLS='):
                updated_lines.append('EMAIL_USE_TLS=True')
            elif line.startswith('EMAIL_HOST_USER='):
                updated_lines.append(f'EMAIL_HOST_USER={email}')
                email_config_found = True
            elif line.startswith('EMAIL_HOST_PASSWORD='):
                updated_lines.append(f'EMAIL_HOST_PASSWORD={password}')
                email_config_found = True
            elif line.startswith('DEFAULT_FROM_EMAIL='):
                updated_lines.append(f'DEFAULT_FROM_EMAIL={email}')
            else:
                updated_lines.append(line)
        
        # Add email config section if not found
        if not email_config_found:
            updated_lines.append('')
            updated_lines.append('# Email Configuration (auto-configured)')
            updated_lines.append(f'EMAIL_HOST={host}')
            updated_lines.append(f'EMAIL_PORT={port}')
            updated_lines.append('EMAIL_USE_TLS=True')
            updated_lines.append(f'EMAIL_HOST_USER={email}')
            updated_lines.append(f'EMAIL_HOST_PASSWORD={password}')
            updated_lines.append(f'DEFAULT_FROM_EMAIL={email}')
        
        # Write updated .env
        env_path.write_text('\n'.join(updated_lines))
        
        self.stdout.write(self.style.SUCCESS('✅ Email configuration saved to .env file!'))
        self.stdout.write(self.style.SUCCESS(f'   EMAIL_HOST_USER={email}'))
        self.stdout.write(self.style.SUCCESS(f'   EMAIL_HOST={host}'))
        self.stdout.write('\n⚠️  Restart Django server for changes to take effect!')

