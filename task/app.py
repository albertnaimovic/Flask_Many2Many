# Sukurti Flask programą, kuri leistų išsaugoti studentus, dėstytojus ir paskaitas
# Kiekvienam dėstytojui leistų priskirti jo paskaitas (one2many ryšys)
# Kiekvienam studentui leistų priskirti daug paskaitų (many2many ryšys)

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, InputRequired
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

# from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

app = Flask(__name__)

app.config["SECRET_KEY"] = "dfgsfdgsdfgsdfgsdf"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite?check_same_thread=False"
)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

association_table = db.Table(
    "association",
    db.metadata,
    db.Column("lecture_id", db.Integer, db.ForeignKey("lecture.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String)
    surname = db.Column("Surname", db.String)
    lectures = db.relationship(
        "Lecture", secondary=association_table, back_populates="students"
    )


class Lecturer(db.Model):
    __tablename__ = "lecturer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String)
    surname = db.Column("Surname", db.String)
    lectures = db.relationship("Lecture")


class Lecture(db.Model):
    __tablename__ = "lecture"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturer.id"))
    lecturer = db.relationship("Lecturer")
    students = db.relationship(
        "Student", secondary=association_table, back_populates="lectures"
    )


def get_pk(obj):
    return str(obj)


with app.app_context():
    db.create_all()

    class StudentForm(FlaskForm):
        name = StringField("Name", [DataRequired()])
        surname = StringField("Surname", [DataRequired()])
        lectures = QuerySelectMultipleField(
            query_factory=Lecture.query.all, get_label="name", get_pk=get_pk
        )
        submit = SubmitField("Enter")

    class LecturerForm(FlaskForm):
        name = StringField("Name", [DataRequired()])
        surname = StringField("Surname", [DataRequired()])
        lectures = QuerySelectMultipleField(
            query_factory=Lecture.query.all, get_label="name", get_pk=get_pk
        )
        submit = SubmitField("Enter")

    class LectureForm(FlaskForm):
        name = StringField("Name", [DataRequired()])
        lecturer = QuerySelectField(
            query_factory=Lecturer.query.all, get_label="name", get_pk=get_pk
        )
        students = QuerySelectMultipleField(
            query_factory=Student.query.all, get_label="name", get_pk=get_pk
        )
        submit = SubmitField("Enter")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_student", methods=["GET", "POST"])
def new_student():
    db.create_all()
    form = StudentForm()
    if form.validate_on_submit():
        new_student = Student(name=form.name.data, surname=form.surname.data)
        for lecture in form.lectures.data:
            assigned_lecture = Lecture.query.get(lecture.id)
            new_student.lectures.append(assigned_lecture)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for("students"))
    return render_template("add_student.html", form=form)


@app.route("/all_students")
def students():
    try:
        all_students = Student.query.all()
    except:
        all_students = []
    return render_template("all_students.html", all_students=all_students)


@app.route("/add_lecturer", methods=["GET", "POST"])
def new_lecturer():
    db.create_all()
    form = LecturerForm()
    if form.validate_on_submit():
        new_lecturer = Lecturer(name=form.name.data, surname=form.surname.data)
        for lecture in form.lectures.data:
            assigned_lecture = Lecture.query.get(lecture.id)
            new_lecturer.lectures.append(assigned_lecture)

        db.session.add(new_lecturer)
        db.session.commit()
        return redirect(url_for("lecturers"))
    return render_template("add_lecturer.html", form=form)


@app.route("/all_lecturers")
def lecturers():
    try:
        all_lecturers = Lecturer.query.all()
    except:
        all_lecturers = []
    return render_template("all_lecturers.html", all_lecturers=all_lecturers)


@app.route("/add_lecture", methods=["GET", "POST"])
def new_lecture():
    db.create_all()
    form = LectureForm()
    if form.validate_on_submit():
        new_lecture = Lecture(name=form.name.data)

        if form.lecturer.data:
            new_lecture.lecturer_id = form.lecturer.data.id

        for student in form.students.data:
            assigned_student = Student.query.get(student.id)
            new_lecture.students.append(assigned_student)

        db.session.add(new_lecture)
        db.session.commit()
        return redirect(url_for("lecturers"))
    return render_template("add_lecture.html", form=form)


@app.route("/all_lectures")
def lectures():
    try:
        all_lectures = Lecture.query.all()
    except:
        all_lectures = []
    return render_template("all_lectures.html", all_lectures=all_lectures)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
