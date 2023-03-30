import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Job, Employee, User, Projects
from mainApp.auth import me, epassword
from . import cache

views = Blueprint('views', __name__)


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
# @cache.cached(timeout=60)
def home():
    return render_template('index.html', user=current_user)


@views.route('/about')
# @cache.cached(timeout=60)
def about():
    return render_template('about.html', user=current_user)


@views.route('/contactus', methods=['GET', 'POST'])
# @cache.cached(timeout=60)
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
# @cache.cached(timeout=60)
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
# @cache.memoize(timeout=60)
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
# @cache.cached(timeout=60)
def employees():
    return render_template('employees.html', user=current_user, all_users=User.query.all(),
                           employees=Employee)


@login_required
@views.route('/job')
# @cache.cached(timeout=60)
def job():
    return render_template('job.html', user=current_user)


@views.route('/jobs')
# @cache.cached(timeout=1800)
def jobs():
    return render_template('jobs.html', user=current_user, jobs=Job.query.all())
