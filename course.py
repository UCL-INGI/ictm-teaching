from decorators import login_required
from db import db, User, Course, Teacher, Organization
from data import LANGUAGES, QUADRI
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, \
    Flask, jsonify, session
import json, re

course_bp = Blueprint('course', __name__)

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)


def validate_course_code(code):
    course_code_regex = r'^[a-zA-Z0-9]+$'
    return re.match(course_code_regex, code) is not None


def validate_course_title(title):
    title_regex = r'^[\w\s,:\']+$'
    return re.match(title_regex, title) is not None


@course_bp.route('/form_course')
@login_required
def form_course():
    current_year = int(request.args.get('current_year'))
    return render_template('add_course.html', quadri=QUADRI, language=LANGUAGES, current_year=current_year)


@course_bp.route('/add_course', methods=['POST'])
@login_required
def add_course():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    current_year = int(request.args.get('current_year'))
    code = request.form['code']
    title = request.form['title']

    if not validate_course_code(code):
        return make_response("Invalid course code", 400)
    if not validate_course_title(title):
        return make_response("Invalid course title", 400)

    quadri = request.form['quadri']
    year = request.form['year']
    language = request.form['language']
    organization_ids = request.form.getlist('organization_code[]')

    try:
        last_course = db.session.query(Course).order_by(Course.id.desc()).first()
        new_id = 1 if last_course is None else last_course.id + 1

        is_course = db.session.query(Course).filter(Course.code == code,
                                                    Course.year == year).first()
        if is_course is not None:
            return make_response("Course already exists", 500)

        new_course = Course(id=new_id, year=year, code=code, title=title, quadri=quadri, language=language)
        # Fetch organizations and add them to the course
        organizations = db.session.query(Organization).filter(Organization.id.in_(organization_ids)).all()
        new_course.organizations.extend(organizations)

        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for("course.form_course", current_year=current_year))
    except Exception as e:
        db.session.rollback()
        raise e


@course_bp.route('/courses')
@login_required
def courses():
    current_year = int(request.args.get('current_year'))
    courses = db.session.query(Course).filter_by(year=current_year).all()
    return render_template('courses.html', courses=courses, current_year=current_year)


@course_bp.route('/search_teachers')
def search_teachers():
    search_term = request.args.get('q', '')
    teachers = db.session.query(User).filter(User.is_teacher == 1, User.name.ilike(f'%{search_term}%')).all()
    results = [{'id': teacher.id, 'text': f'{teacher.name} {teacher.first_name}'} for teacher in teachers]
    return jsonify(results)


@course_bp.route('<int:course_id>')
@login_required
def course_info(course_id):
    current_year = int(request.args.get('current_year'))
    course = db.session.query(Course).filter(Course.id == course_id, Course.year == current_year).first()
    if not course:
        return make_response("Course not found", 404)

    all_years = db.session.query(Course).filter_by(id=course.id).distinct(Course.year).order_by(
        Course.year.desc()).all()
    return render_template('course_info.html', course=course, all_years=all_years, quadri=QUADRI,
                           language=LANGUAGES, current_year=current_year)


@course_bp.route('/update_course_info', methods=['POST'])
@login_required
def update_course_info():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    current_year = int(request.args.get('current_year'))
    code = request.form['code']
    title = request.form['title']
    if not validate_course_code(code):
        return make_response("Invalid course code", 400)
    if not validate_course_title(title):
        return make_response("Invalid course title", 400)

    course_id = request.form['course_id']
    quadri = request.form['quadri']
    year = request.form['year']
    language = request.form['language']
    assigned_teachers = request.form.getlist('assigned_teachers[]')
    organisation_code = request.form.getlist('organization_code[]')
    nbr_students = request.form['nbr_students']
    nbr_teaching_assistants = request.form['nbr_teaching_assistants']
    nbr_monitor_students = request.form['nbr_monitor_students']

    course = db.session.query(Course).filter(Course.id == course_id, Course.year == year).first()
    if not course:
        return make_response("Course not found", 404)

    # Remove all teachers assigned to the course
    db.session.query(Teacher).filter(Teacher.course_id == course_id, Teacher.course_year == year).delete()
    course.course_teacher.clear()

    # Add new teachers to the course
    if assigned_teachers:
        try:
            for teacher_id in assigned_teachers:
                new_teacher = Teacher(user_id=teacher_id, course_id=course_id, course_year=year)
                db.session.add(new_teacher)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    try:
        course.code = code
        course.title = title
        course.quadri = quadri
        course.year = year
        course.language = language
        course.nbr_students = nbr_students
        course.nbr_teaching_assistants = nbr_teaching_assistants
        course.nbr_monitor_students = nbr_monitor_students

        course.organizations.clear()
        course.organizations = db.session.query(Organization).filter(
            Organization.id.in_(organisation_code)).all()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for("course.course_info", course_id=course_id, current_year=current_year))


@course_bp.route('/duplicate_course')
@login_required
def duplicate_course():
    course_id = request.args.get('course_id')
    course_year = request.args.get('year')
    course = db.session.query(Course).filter(Course.id == course_id, Course.year == course_year).first()
    current_year = int(request.args.get('current_year'))

    return render_template('duplicate_course.html', course=course, quadri=QUADRI, language=LANGUAGES, current_year=current_year)


@course_bp.route('/add_duplicate_course', methods=['POST'])
@login_required
def add_duplicate_course():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    current_year = int(request.args.get('current_year'))
    code = request.form['code']
    title = request.form['title']
    if not validate_course_code(code):
        return make_response("Invalid course code", 400)
    if not validate_course_title(title):
        return make_response("Invalid course title", 400)

    course_id = request.form['course_id']
    quadri = request.form['quadri']
    year = request.form['year']
    language = request.form['language']
    assigned_teachers = request.form.getlist('assigned_teachers[]')
    organisation_code = request.form.getlist('organization_code[]')
    nbr_students = request.form['nbr_students']
    nbr_teaching_assistants = request.form['nbr_teaching_assistants']
    nbr_monitor_students = request.form['nbr_monitor_students']

    try:
        duplicate_course = Course(id=course_id, code=code, title=title, quadri=quadri, year=year,
                                  language=language, nbr_students=nbr_students,
                                  nbr_teaching_assistants=nbr_teaching_assistants,
                                  nbr_monitor_students=nbr_monitor_students)
        organizations = db.session.query(Organization).filter(Organization.id.in_(organisation_code)).all()
        duplicate_course.organizations.extend(organizations)
        db.session.add(duplicate_course)

        for teacher_id in assigned_teachers:
            duplicate_teacher = Teacher(user_id=teacher_id, course_id=course_id, course_year=year)
            db.session.add(duplicate_teacher)

        db.session.commit()

    except Exception as e:
        db.session.rollback()

    return redirect(url_for('course.course_info', course_id=course_id, current_year=current_year))
