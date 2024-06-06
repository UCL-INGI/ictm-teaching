from decorators import login_required
from db import db, User, Course, Teacher, Configuration, Organization
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, \
    Flask, jsonify, session
import json

course_bp = Blueprint('course', __name__)

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
with open('config.json') as config_file:
    app.config.update(json.load(config_file))

# List from config.json
quadri = app.config.get('quadri', [])
year = app.config.get('year', [])
language = ['fr', 'en']


@course_bp.route('/form_course')
@login_required
def form_course():
    return render_template('add_course.html', quadri=quadri, language=language)


@course_bp.route('/add_course', methods=['POST'])
@login_required
def add_course():
    form = request.form
    if form:
        code = request.form['code']
        title = request.form['title']
        quadri = request.form['quadri']
        year = request.form['year']
        language = request.form['language']
        organization_ids = request.form.getlist('organization_code[]')

        try:
            last_course = db.session.query(Course).order_by(Course.id.desc()).first()
            if last_course is None:
                new_id = 1
            else:
                new_id = last_course.id + 1

            is_course = db.session.query(Course).filter(Course.code == code,
                                                        Course.year == year).first()
            if is_course is None:
                new_course = Course(id=new_id, year=year, code=code, title=title, quadri=quadri, language=language)
                # Fetch organizations and add them to the course
                organizations = db.session.query(Organization).filter(Organization.id.in_(organization_ids)).all()
                new_course.organizations.extend(organizations)

                db.session.add(new_course)
                db.session.commit()
                return redirect(url_for("course.form_course"))
            else:
                flash('Course already exists', 'warning')
        except Exception as e:
            db.session.rollback()
            raise e

    # Redirect to the course form if form submission fails or course already exists
    return redirect(url_for("course.form_course"))


@course_bp.route('/courses')
@login_required
def courses():
    current_year = session["current_year"]
    courses = db.session.query(Course).filter_by(year=current_year).all()
    return render_template('courses.html', courses=courses)


@course_bp.route('/search_teachers')
def search_teachers():
    search_term = request.args.get('q', '')
    teachers = db.session.query(User).filter(User.is_teacher == 1, User.name.ilike(f'%{search_term}%')).all()
    results = [{'id': teacher.id, 'text': f'{teacher.name} {teacher.first_name}'} for teacher in teachers]
    return jsonify(results)


@course_bp.route('<int:course_id>')
@login_required
def course_info(course_id):
    current_year = session["current_year"]
    course = db.session.query(Course).filter(Course.id == course_id, Course.year == current_year).first()

    if course:
        all_years = db.session.query(Course).filter_by(id=course.id).distinct(Course.year).order_by(
            Course.year.desc()).all()
        return render_template('course_info.html', course=course, all_years=all_years, quadri=quadri,
                               language=language)
    else:
        flash('Course not found', 'error')
        return redirect(url_for('course.courses'))


@course_bp.route('/update_course_info', methods=['POST'])
@login_required
def update_course_info():
    form = request.form
    if form:
        course_id = request.form['course_id']
        code = request.form['code']
        title = request.form['title']
        quadri = request.form['quadri']
        year = request.form['year']
        load_needed = request.form['load_needed']
        language = request.form['language']
        assigned_teachers = request.form.getlist('assigned_teachers[]')
        organisation_code = request.form.getlist('organization_code[]')
        nbr_students = request.form['nbr_students']
        nbr_teaching_assistants = request.form['nbr_teaching_assistants']
        nbr_monitor_students = request.form['nbr_monitor_students']

        course = db.session.query(Course).filter(Course.id == course_id, Course.year == year).first()
        if assigned_teachers:
            try:
                teachers_to_remove = db.session.query(Teacher).filter(Teacher.course_id == course_id,
                                                                      Teacher.course_year == year,
                                                                      ~Teacher.user_id.in_(assigned_teachers)).all()
                # Get rid of teachers who no longer teach the course
                for teacher in teachers_to_remove:
                    db.session.delete(teacher)
                    db.session.commit()

                for teacher in assigned_teachers:
                    is_teacher = db.session.query(Teacher).filter(Teacher.course_id == course_id,
                                                                  Teacher.user_id == teacher,
                                                                  Teacher.course_year == year).first()
                    # Check that you are not adding an existing teacher
                    if is_teacher is None:
                        new_teacher = Teacher(user_id=teacher, course_id=course_id, course_year=year)
                        db.session.add(new_teacher)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        if course:
            try:
                course.code = code
                course.title = title
                course.quadri = quadri
                course.year = year
                course.load_needed = load_needed
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
            return redirect(url_for("course.course_info", course_id=course_id))
        else:
            flash('Course not found', 'danger')
    else:
        return make_response("Problem with form request", 500)


@course_bp.route('/duplicate_course')
@login_required
def duplicate_course():
    course_id = request.args.get('course_id')
    course_year = request.args.get('year')
    course = db.session.query(Course).filter(Course.id == course_id, Course.year == course_year).first()

    return render_template('duplicate_course.html', course=course, quadri=quadri, language=language)


@course_bp.route('/add_duplicate_course', methods=['POST'])
@login_required
def add_duplicate_course():
    if request.method == 'POST':
        form = request.form
        if form:
            course_id = request.form['course_id']
            code = request.form['code']
            title = request.form['title']
            quadri = request.form['quadri']
            year = request.form['year']
            load_needed = request.form['load_needed']
            language = request.form['language']
            assigned_teachers = request.form.getlist('assigned_teachers[]')
            organisation_code = request.form.getlist('organization_code[]')
            nbr_students = request.form['nbr_students']
            nbr_teaching_assistants = request.form['nbr_teaching_assistants']
            nbr_monitor_students = request.form['nbr_monitor_students']

            try:
                duplicate_course = Course(id=course_id, code=code, title=title, quadri=quadri, year=year,
                                          load_needed=load_needed, language=language, nbr_students=nbr_students,
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

        return redirect(url_for('course.course_info', course_id=course_id))
