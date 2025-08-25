from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .settings import settings
from .db import get_db
from .models import User
ALGO='HS256'

def get_current_user(authorization:str|None=Header(default=None), db:Session=Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Missing Bearer token')
    token = authorization.split()[1]
    try: payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
    except JWTError: raise HTTPException(status_code=401, detail='Invalid token')
    email = payload.get('sub');
    user = db.query(User).filter(User.email==email).first()
    if not user: raise HTTPException(status_code=401, detail='User not found')
    return user
