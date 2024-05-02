from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    admin = db.Column(db.Boolean, default=False)

