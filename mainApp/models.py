from flask_login import UserMixin
import datetime
from . import db

employee_project = db.Table('employee_project',
                            db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
                            db.Column('project_id', db.Integer, db.ForeignKey('projects.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    firstName = db.Column(db.String(50), nullable=False)
    middleName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(12), nullable=False)
    img = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    EMPLOYEE = db.relationship('Employee', back_populates='user', cascade='all,delete-orphan', viewonly=True)
    APPLICANT = db.relationship('Applicant', cascade='all,delete-orphan')


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    date_employed = db.Column(db.Date, default=datetime.date.today())
    about = db.Column(db.String(150), default="No description")
    skills = db.Column(db.String(100), default="Not assessed")
    performance = db.Column(db.String(100), default="Not assessed")
    work_email = db.Column(db.String(50))
    isManager = db.Column(db.Boolean, default=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    PROJECT = db.relationship('Projects', secondary=employee_project, backref='em_projects')
    employees = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]))
    user = db.relationship('User', back_populates="EMPLOYEE", viewonly=True)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    projects = db.relationship('Projects', backref='client')


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    project_description = db.Column(db.String(300), default='No description')
    date_commenced = db.Column(db.Date)
    date_completed = db.Column(db.Date, default=None)
    isCompleted = db.Column(db.Boolean, default=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), default="0")


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    isAvailable = db.Column(db.Boolean, default=True)
    job_description = db.Column(db.String(300), default='No information')
    salary = db.Column(db.Integer)
    skills = db.Column(db.String(100))
    startApply = db.Column(db.Date, default=datetime.date.today())
    endApply = db.Column(db.Date, default=None)
    type = db.Column(db.String(10), default="Full time")
    EMPLOYEE = db.relationship('Employee', backref='employee', cascade='all,delete-orphan')
    APPLICANT = db.relationship('Applicant', backref='job', cascade='all,delete-orphan')


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    date_submitted = db.Column(db.Date, default=datetime.date.today())
    status = db.Column(db.String(100), default="Pending Review")
    resume = db.Column(db.String(100), nullable=False)
    cover_file = db.Column(db.String(100), nullable=False)
