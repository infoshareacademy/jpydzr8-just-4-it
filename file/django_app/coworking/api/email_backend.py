"""
Custom SMTP Email Backend with SSL certificate verification disabled for development
"""
import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend
from django.core.mail.utils import DNS_NAME
from django.conf import settings


class DevSMTPEmailBackend(BaseEmailBackend):
    """
    SMTP email backend that disables SSL certificate verification for development.
    WARNING: Only use this in development, not in production!
    """
    
    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False), or None if an
        existing connection was used.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return None

        connection_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {'local_hostname': DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl:
            # For SSL, we need to create a custom SSL context that doesn't verify certificates
            # WARNING: This is only for development!
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connection_params['context'] = ssl_context
        try:
            self.connection = connection_class(
                self.host, self.port, **connection_params
            )
            # Set TLS connection to not verify certificates
            if self.use_tls and not self.use_ssl:
                # For STARTTLS, we need to set the SSL context before calling starttls
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                self.connection.starttls(context=ssl_context)
            # Authenticate
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

