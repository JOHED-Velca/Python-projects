from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from db.sessions import engine


Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    url = Column(String(500))
    description = Column(Text, nullable=False)


# Simple one-time table creation for step 1 (replace with Alembic later)
Base.metadata.create_all(bind=engine)