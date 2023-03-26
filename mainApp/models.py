from flask_login import UserMixin
import datetime
from . import db

employee_project = db.Table('employee_project',
                            db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
                            db.Column('project_id', db.Integer, db.ForeignKey('projects.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    middleName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(12), nullable=False)
    img = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    EMPLOYEE = db.relationship('Employee', cascade='all,delete-orphan')
    APPLICANT = db.relationship('Applicant', cascade='all,delete-orphan')


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    date_employed = db.Column(db.Date, default=datetime.date.today())
    about = db.Column(db.String(150), default="No description")
    skills = db.Column(db.String(100), default="Not assessed")
    performance = db.Column(db.String(100), default="Not assessed")
    work_email = db.Column(db.String(50))
    isManager = db.Column(db.Boolean, default=False)
    PROJECT = db.relationship('Projects', secondary=employee_project, backref='em_projects')


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    project_description = db.Column(db.String(300), default='No description')
    contributors = db.Column(db.String(300), default='No contributors')
    manager = db.Column(db.String(200), default='No manager')
    date_commenced = db.Column(db.Date)
    isCompleted = db.Column(db.Boolean, default=False)
    date_completed = db.Column(db.Date, default=None)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    isAvailable = db.Column(db.Boolean, default=True)
    job_description = db.Column(db.String(300), default='No information')
    manager = db.Column(db.String(200), default='C.E.O')
    salary = db.Column(db.Integer)
    skills = db.Column(db.String(100))
    startApply = db.Column(db.Date, default=datetime.date.today())
    endApply = db.Column(db.Date, default=None)
    type = db.Column(db.String(10), default="Full time")
    EMPLOYEE = db.relationship('Employee', backref='employee', cascade='all,delete-orphan')
    APPLICANT = db.relationship('Applicant', backref='applicant', cascade='all,delete-orphan')


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    applicant_job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    isSubscribed = db.Column(db.Boolean, default=False)
    date_submitted = db.Column(db.Date, default=datetime.date.today())
    resume = db.Column(db.String(100), default=None)