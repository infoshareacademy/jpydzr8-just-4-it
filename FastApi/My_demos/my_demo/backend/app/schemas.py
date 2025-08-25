from pydantic import BaseModel, EmailStr
from typing import Optional, List
class UserCreate(BaseModel): email: EmailStr; password: str; full_name: Optional[str]=None
class UserOut(BaseModel): id:int; email:EmailStr; full_name:Optional[str]=None
class TokenOut(BaseModel): access_token:str; token_type:str='bearer'
class LoginReq(BaseModel): email:EmailStr; password:str
class ReservationCreate(BaseModel): seat_id:str; date:str; name:str; email:str; notes:Optional[str]=''
class ReservationOut(BaseModel): id:str; seat_id:str; date:str; name:str; email:str; notes:Optional[str]=''; created_at:str
