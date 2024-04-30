from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    organization_code = db.Column(db.String, nullable=True)
    admin = db.Column(db.Boolean, default=False)

class Course(db.Model):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    organization_code = Column(String)
    title = Column(String)
    quadri = Column(Integer)
    year = Column(String)
    load_needed = Column(Integer)

# Ajouter le premier admin dans la base de données
def add_first_admin():
    session = Session()
    admin_exists = session.query(User).filter_by(admin=True).first()
    if admin_exists is None:
        first_admin = User(name='Admin', first_name='Admin', email='admin@example.com', organization_code="", admin=True)
        session.add(first_admin)
        session.commit()

add_first_admin()
