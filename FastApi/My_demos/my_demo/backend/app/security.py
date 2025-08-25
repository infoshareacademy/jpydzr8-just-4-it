from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from .settings import settings
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGO='HS256'

def hash_password(p): return pwd_context.hash(p)

def verify_password(p, h): return pwd_context.verify(p, h)

def create_access_token(sub, minutes=None):
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({'sub':sub,'exp':exp}, settings.SECRET_KEY, algorithm=ALGO)
