from fastapi import FastAPI,HTTPException,Request,status,Response
from pydantic import BaseModel
from typing import List
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import Base,get_db,engine
from .models import Note,User
from  .auth import (create_access_token,get_current_user,create_refresh_token,verify_password,hash_password)
import uuid

app=FastAPI(title="Note Taking Application")

Base.metadata.create_all(bind=engine)
class SignupRequest(BaseModel):
    username:str
    password:str
class LoginRequest(BaseModel):
    username:str
    password:str

class NoteCreate(BaseModel):
    title:str
    content:str
        
class Notes(BaseModel):
    id:str
    title:str
    content:str
    date_of_creation:datetime
    
    
    class Config:
        from_attributes=True
        
        
@app.get("/")
def home():
    return{"message":"Simple Notes","version":"2.0"}

@app.post("/signup",status_code=201)
def signup(
    data:SignupRequest,
    db:Session=Depends(get_db)
):
    existing_user=db.query(User).filter(User.username==data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
    hashed_pass=hash_password(data.password)
    
    user=User(id=str(uuid.uuid4()),username=data.username,hashed_password=hashed_pass)
    db.add(user)
    db.commit()
    db.refresh(user)
    return{"message":"USER REGISTERED SUCCESSFULLY"}

@app.post("/login")
def login(
    data:LoginRequest,
    response:Response,
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(User.username==data.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")
    if not verify_password(data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")
    access_token=create_access_token(user.id)
    refresh_token=create_refresh_token()
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return{
        "access_token":access_token,
        "token_type":"bearer"
    }


@app.post("/notes",response_model=Notes,status_code=201)
def created_note(note:NoteCreate,user_id:str=Depends(get_current_user),db:Session=Depends(get_db)):
    new_note=Note(
        title=note.title,
        content=note.content
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@app.get("/notes",response_model=List[Notes])
def get_notes(user_id:str=Depends(get_current_user),db:Session =Depends(get_db)):
    return db.query(Note).all()


@app.get("/notes/{notes_id}",response_model=Notes)
def get_note(notes_id:str,db:Session=Depends(get_db)):
    note=db.query(Note).filter(Note.id==notes_id).first()
    if note is None:
        raise HTTPException(status_code=404,detail="Note not found")
    return note


@app.put("/notes/{notes_id}",response_model=Notes)
def update_note(notes_id:str ,update_note:NoteCreate,db:Session=Depends(get_db)):
    note=db.query(Note).filter(Note.id==notes_id).first()
    if note is None:
        raise HTTPException(status_code=404,detail="Note not found")
    
    note.title=update_note.title
    note.content=update_note.content
    
    db.commit()
    db.refresh(note)
    return note
@app.delete("/notes/{notes_id}")
def delete_note(notes_id:str,db:Session=Depends(get_db)):
    note=db.query(Note).filter(Note.id==notes_id).first()
    
    if note is None:
        raise HTTPException(status_code=404,detail="Note not found")
    
    db.delete(note)
    db.commit()
    return{"message":"NOTE DELETED"}

@app.post("/ping")
def ping(data: dict):
    return {"received": data,"timestamp":datetime.utcnow()}

@app.post("/refresh")
def refresh_token(request:Request):
    refresh_token=request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Refresh token is missing")
    
    user_id="test_user"
    
    new_access_token=create_access_token(user_id)
    
    return{
        "access_token":new_access_token,
        "token_type":"bearer"
    }