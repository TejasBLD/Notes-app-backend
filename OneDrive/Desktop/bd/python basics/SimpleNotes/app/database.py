from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,declarative_base

engine=create_engine("sqlite:///notes.db",echo=True,connect_args={"check_same_thread":False})

SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base= declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    