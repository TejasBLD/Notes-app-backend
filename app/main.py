from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Note

app=FastAPI(title="Note Taking Application")


class NoteCreate(BaseModel):
    title:str
    content:str
    
    
class Notes(BaseModel):
    id:str
    title:str
    content:str
    date_of_creation:datetime
    
    
    class Config:
        orm_mode=True
        
        
@app.get("/")
def home():
    return{"message":"Simple Notes","version":"2.0"}


@app.post("/notes",response_model=Notes,status_code=201)
def created_note(note:NoteCreate,db:Session=Depends(get_db)):
    new_note=Note(
        title=note.title,
        content=note.content
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@app.get("/notes",response_model=List[Notes])
def get_notes(db:Session =Depends(get_db)):
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
