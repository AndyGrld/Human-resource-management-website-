import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from models import Job, Employee, User

from mainApp.auth import me, epassword

views = Blueprint('views', __name__)


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
    employee = Employee.query.filter_by(emp_id=current_user.id).first()
    return render_template('mydashboard.html', user=current_user, employee=employee)


@views.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', user=current_user)


@login_required
@views.route('/employees')
def employees():
    return render_template('employees.html', user=current_user, all=User.query.all(),
                           employees=Employee.query.all())


@login_required
@views.route('/job')
def job():
    return render_template('job.html', user=current_user)


@views.route('/jobs')
def jobs():
    return render_template('jobs.html', user=current_user, jobs=Job)
