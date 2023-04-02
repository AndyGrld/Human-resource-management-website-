import smtplib
import os
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Job, Employee, User, Projects, Applicant
from mainApp.auth import me, epassword
from . import db, cache

views = Blueprint('views', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}


def get_managed_employees(employee_id):
    employee = Employee.query.get(employee_id)
    if employee:
        managed_employees = Employee.query.filter(Employee.isManager==False, Employee.id!=employee.id, Employee.PROJECT.any(Projects.em_projects.any(Employee.id==employee.id))).all()
        return managed_employees
    else:
        return None


def get_managers(employee_id):
    employee = Employee.query.get(employee_id)
    if employee:
        managers = Employee.query.filter_by(isManager=True).filter(Employee.PROJECT.any(Projects.em_projects.any(Employee.id==employee.id))).all()
        return managers
    else:
        return None


def send_mail(name, user_email, tel, subject, body):
    message = MIMEMultipart()
    message['subject'] = subject
    message['from'] = user_email
    message['to'] = me
    message.attach(MIMEText(f"{body}\nName: {name}\nPhone: 0{tel}"))
    try:
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        server.ehlo()
        server.starttls()
        server.login(me, epassword)
        server.sendmail(user_email, me, message.as_string())
        server.quit()
        flash("Message sent, please check your email account", category="success")
    except Exception as e:
        flash("Could not send message, please try again", category="error")


@views.route('/')
def home():
    return render_template('index.html', user=current_user)


@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


@views.route('/contactus', methods=['GET', 'POST'])
def contactUs():
    if request.method == 'POST':
        name = request.form.get('name')
        tel = request.form.get('tel')
        email = request.form.get('email')
        subject = request.form.get('subject')
        body = request.form.get('message')
        send_mail(name, email, tel, subject, body)
    return render_template('contactus.html', user=current_user)


@login_required
@views.route('/mydashboard')
def mydashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    job = Job.query.filter_by(id=employee.job_id).first()
    project = employee.PROJECT
    managed_employees = get_managed_employees(employee.id)
    managers = get_managers(employee.id)
    return render_template('mydashboard.html', user=current_user, employee=employee, project=project, job=job,
                           managed_employees=managed_employees, managers=managers)


@views.route('/dashboard/<int:id>')
@login_required
def dashboard(id):
    if id == current_user.id:
        return redirect(url_for('views.mydashboard'))
    other = User.query.filter_by(id=id).first()
    employee = Employee.query.filter_by(user_id=other.id).first()
    job = Job.query.filter_by(id=employee.job_id).first()
    project = employee.PROJECT
    managed_employees = get_managed_employees(employee.id)
    managers = get_managers(employee.id)
    return render_template('dashboard.html', user=current_user, other=other, employee=employee, project=project,
                           job=job, managed_employees=managed_employees, managers=managers)


@login_required
@views.route('/employees')
def employees():
    return render_template('employees.html', user=current_user, all_users=User.query.all(),
                           employees=Employee)


@login_required
@views.route('/job/<int:id>', methods = ['GET', 'POST'])
def job(id):
    job = Job.query.filter_by(id=id).first()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please login to apply for a job', category='error')
            return redirect(url_for('auth.login'))
        resume_file = request.files['resume']
        cover_file = request.files['cover_file']
        if resume_file and allowed_file(resume_file.filename) and cover_file and allowed_file(cover_file.filename):
            # save uploaded files with unique filenames
            resume_filename = secure_filename(resume_file.filename)
            cover_filename = secure_filename(cover_file.filename)
            resume_file.save(os.path.join("mainApp/static/files/resume", resume_filename))
            cover_file.save(os.path.join("mainApp/static/files/cover_file", cover_filename))
            # create new applicant record in database
            new_applicant = Applicant(user_id=current_user.id, job_id=id, resume=resume_filename, cover_file=cover_filename)
            db.session.add(new_applicant)
            db.session.commit()
            flash('Your application has been sent successfully', category='success')
            return redirect(url_for('views.job', id=id))
        else:
            flash('Please upload PDF or Word files only.', category='error')
    return render_template('job.html', user=current_user, job=job)


@views.route('/jobs')
@login_required
def jobs():
    return render_template('jobs.html', user=current_user, jobs=Job.query.all())


@views.route('/subscribe')
def subscribe():
    if current_user.isSubscribed:
        current_user.isSubscribed = False
        db.session.commit()
        flash("Unsubscribed", category='error')
        return redirect(url_for("views.home"))
    else:
        current_user.isSubscribed = True
        db.session.commit()
        flash("Subscription successful", category='success')
        return redirect(url_for("views.home"))
