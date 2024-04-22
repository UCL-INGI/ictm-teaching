from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, query

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    admin = Column(Boolean, default=False)


# Création de la base de données
engine = create_engine('sqlite:///ictm-teaching.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
