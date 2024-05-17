from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

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


class Configuration(db.Model):
    __tablename__ = 'configuration'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String, nullable=False)
    is_current_year = db.Column(db.Boolean, default=True)

    @classmethod
    def update_current_year(cls, config_id):
        # Update all years to set is_current_year to False
        cls.query.update({cls.is_current_year: False})

        selected_config = cls.query.get(config_id)
        if selected_config:
            selected_config.is_current_year = True
            db.session.commit()


# Add the first admin to the database
def add_first_admin():
    admin_exists = db.session.query(User).filter_by(admin=True).first()
    if admin_exists is None:
        first_admin = User(name='Admin', first_name='Admin', email='admin@example.com', organization_code="",
                           admin=True)
        db.session.add(first_admin)
        db.session.commit()


def get_current_academic_year():
    current_year = datetime.now().year
    next_year = current_year + 1
    academic_year = f"{current_year}-{next_year}"
    return academic_year


# Add the first year corresponding to the current year
def initialize_configuration():
    current_year = get_current_academic_year()
    existing_year = Configuration.query.filter_by(year=current_year).first()

    if existing_year is None:
        config = Configuration(year=current_year)
        db.session.add(config)
        db.session.commit()
