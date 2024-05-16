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
    is_teacher = db.Column(db.Boolean, default=False)
    is_researcher = db.Column(db.Boolean, default=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    supervisor = db.relationship('User', remote_side=[id], backref='supervisees')


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String, primary_key=True)
    code = db.Column(db.String)
    organization_code = db.Column(db.String)
    title = db.Column(db.String)
    quadri = db.Column(db.Integer)
    load_needed = db.Column(db.Integer, default=0)
    language = db.Column(db.String)


class Researcher(db.Model):
    __tablename__ = 'researcher'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    research_field = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)
    max_loads = db.Column(db.Integer)
    jokers = db.Column(db.Integer)
    researcher_type = db.Column(db.String)

    user = db.relationship('User', backref=db.backref('user_researcher', lazy=True))


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    course_year = db.Column(db.String, nullable=False)

    # Creation of a link to the compound key (id, year) of the course table
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['course_id', 'course_year'],
            ['course.id', 'course.year']
        ),
    )

    user = db.relationship('User', backref=db.backref('user_teacher', lazy=True))
    course = db.relationship('Course', backref=db.backref('course_teacher', lazy=True))


class PreferenceAssignment(db.Model):
    __tablename__ = 'preference_assignment'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.id'), nullable=False)

    course = db.relationship('Course', backref=db.backref('course_preference_assignment', lazy=True))
    researcher = db.relationship('Researcher', backref=db.backref('researcher_preference_assignment', lazy=True))

