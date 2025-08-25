from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .schemas import UserCreate, UserOut, LoginReq, TokenOut
from .security import hash_password, verify_password, create_access_token
from .deps import get_current_user
router = APIRouter(prefix='/api/auth', tags=['auth'])
@router.post('/register', response_model=UserOut)
def register(p:UserCreate, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==p.email).first(): raise HTTPException(status_code=400, detail='User already exists')
    u=User(email=p.email, password_hash=hash_password(p.password), full_name=p.full_name or '')
    db.add(u); db.commit(); db.refresh(u); return u
@router.post('/login', response_model=TokenOut)
def login(p:LoginReq, db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==p.email).first()
    if not u or not verify_password(p.password, u.password_hash): raise HTTPException(status_code=401, detail='Invalid credentials')
    return {'access_token': create_access_token(u.email), 'token_type':'bearer'}
@router.get('/me', response_model=UserOut)
def me(user:User=Depends(get_current_user)): return user
