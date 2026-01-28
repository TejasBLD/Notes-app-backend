from passlib.context import CryptContext
from datetime import datetime,timedelta
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
import secrets


context=CryptContext(schemes=["bcrypt"],deprecated="auto")
Secret_key="18c586b7542e50bf12e271b2ca9c1adc"
Algorithm="HS256"
Access_token_expire_minutes=10
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password:str)->str:
    return context.hash(password)

def verify_password(password:str,h_password:str)->bool:
    return context.verify(password,h_password)

def create_access_token(user_id:str)->str:
    expire=datetime.utcnow()+timedelta(minutes=Access_token_expire_minutes)
    payload={
        "sub":user_id,
        "exp":expire
    }
    token=jwt.encode(payload,Secret_key,algorithm=Algorithm)
    return token

def verify_access_token(token:str)->str:
    try:
        payload=jwt.decode(token,Secret_key,algorithms=[Algorithm])
        user_id=payload.get("sub")
        
        if user_id is None:
            raise ValueError("Invalid token payload")
        
        return user_id
    except JWTError:
        raise ValueError("Invalid or expired token")
def get_current_user(token:str = Depends(oauth2_scheme))->str:
    try:
        user_id=verify_access_token(token)
        return user_id
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,details="INVALID OR EXPIRED TOKEN",headers={"WWW-Authentication":"Bearer"})
    
def create_refresh_token()->str:
    return secrets.token_urlsafe(32)
