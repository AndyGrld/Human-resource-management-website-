from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html', user=current_user)


@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


@views.route('/contactus')
def contactUs():
    return render_template('contactus.html', user=current_user)


@views.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', user=current_user)


@views.route('/employees')
def employees():
    return render_template('employees.html', user=current_user)


@views.route('/job')
def job():
    return render_template('job.html', user=current_user)


@views.route('/jobs')
def jobs():
    return render_template('jobs.html', user=current_user)
