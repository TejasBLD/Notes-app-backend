from .database import Base
from sqlalchemy import Column,String,Text,DateTime
from datetime import datetime
import uuid
class Note(Base):
    __tablename__="notes"
    id=Column(
        String,
        primary_key=True,
        default=lambda:str(uuid.uuid4())
    )
    title=Column(
        String,
        nullable=False
    )
    content=Column(
        Text,
        nullable=False
    )
    date_of_creation=Column(
        DateTime,
        datetime,default=datetime.now
    )