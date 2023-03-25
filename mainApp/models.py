from flask_login import UserMixin
import datetime
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    firstName = db.Column(db.String(50))
    middleName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    phone = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(12))
    img = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    EMPLOYEE = db.relationship('Employee', cascade='all,delete-orphan')
    APPLICANT = db.relationship('Applicant', cascade='all,delete-orphan')


class Employee(db.Model):
    emp_id = db.Column(db.Integer, db.Foreignkey("user.id"))
    date_employed = db.Column(db.Date)
    skills = db.Column(db.String(100))
    isManager = db.Column(db.Boolean, default=False)
    JOB = db.relationship('Jobs')
    PROJECT = db.relationship('Projects')


class Projects(db.Model):
    project_id = db.Column(db.Integer, db.Foreignkey('employee.emp_id'))
    name = db.Column(db.String(50), nullable=False)
    project_description = db.Column(db.String(300), default='No description')
    contributors = db.Column(db.String(300), default='No contributors')
    manager = db.Column(db.String(200), default='No manager')
    date_commenced = db.Column(db.Date)
    date_completed = db.Column(db.Date, default=None)


class Job(db.Model):
    job_id = db.Column(db.Integer, db.Foreignkey('employee.emp_id'))
    name = db.Column(db.String(50), nullable=False)
    job_description = db.Column(db.String(300), default='No information')
    manager = db.Column(db.String(200), default='C.E.O')
    salary = db.Integer(db.Integer)
    type = db.Column(db.String(10), default="Full time")


class Applicant(db.Model):
    applicant_id = db.Column(db.Integer, db.Foreignkey('user.id'))
    isSubscribed = db.Column(db.Boolean, default=False)
    date_submitted = db.Column(db.Date, default=datetime.date.today())
    resume = db.Column(db.String(100), default=None)
