from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from .models import User, Employee, Client, Projects, Job, Applicant
from email.mime.text import MIMEText
from mainApp.models import User
from . import db, cache
import mediapipe as mp
import uuid as uuid
import cv2 as cv
import smtplib
import os

auth = Blueprint('auth', __name__)

with open(r'password.txt', 'r') as file:
    epassword = file.readline()
    me = file.readline()
    epassword = epassword.rstrip()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}


def send_mail(C_user):
    you = C_user.email
    message = MIMEMultipart()
    message['subject'] = "Welcome to UMat"
    message['from'] = me
    message['to'] = you
    message.attach(MIMEText(f"Your account has been successfully created"))
    try:
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        server.ehlo()
        server.starttls()
        server.login(me, epassword)
        server.sendmail(me, you, message.as_string())
        server.quit()
        db.session.add(C_user)
        db.session.commit()
    except Exception as e:
        flash("Could not process form, Please try again", category="error")
        return render_template('signup.html', user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
# @cache.cached(timeout=60)
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass1')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Account does not exist', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/admin')
@login_required
# @cache.cached(timeout=60)
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))
    return render_template('admin/admin.html', now=current_user, users=User.query.all())


@auth.route('/showEmployees')
def showEmployees():
    employees = Employee.query.all()
    return render_template('admin/showEmployees.html', employees=employees)


@auth.route('/showClients')
def showClients():
    clients = Client.query.all()
    return render_template('admin/showClients.html', clients=clients)


@auth.route('/showProjects')
def showProjects():
    projects = Projects.query.all()
    return render_template('admin/showProjects.html', projects=projects)


@auth.route('/showJobs')
def showJobs():
    jobs = Job.query.all()
    return render_template('admin/showJobs.html', jobs=jobs)


@auth.route('/showUsers')
def showUsers():
    users = User.query.all()
    return render_template('admin/showUsers.html', users=users)


@auth.route('/editUser/<int:id>', methods = ['GET', 'POST'])
@login_required
def editUser(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.firstName = request.form['firstName']
        user.middleName = request.form['middleName']
        user.lastName = request.form['lastName']
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.date_of_birth = request.form['date_of_birth']
        user.img = request.form['img']
        user.is_superuser = True if request.form.get('is_superuser') else False
        user.is_admin = True if request.form.get('is_admin') else False
        user.isSubscribed = True if request.form.get('isSubscribed') else False
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully', 'success')
    return render_template('admin_edit/editUser.html', user=user)


@auth.route('/editEmployee/<int:id>', methods=['GET', 'POST'])
@login_required
def editEmployee(id):
    employee = Employee.query.get_or_404(id)
    projects = Projects.query.all()
    if request.method == 'POST':
        employee.about = request.form['about']
        employee.skills = request.form['skills']
        employee.performance = request.form['performance']
        employee.work_email = request.form['work_email']
        employee.isManager = True if request.form.get('isManager') else False
        employee.manager_id = request.form['manager_id']
        employee.PROJECT = [Projects.query.get(project_id) for project_id in request.form.getlist('PROJECT')]
        db.session.commit()
        flash('Employee updated successfully.', 'success')
        return redirect(url_for('auth.editEmployee', id=id))
    return render_template('admin_edit/editEmployee.html', employee=employee, projects=projects)


@auth.route('/editClient/<int:id>', methods=['GET', 'POST'])
@login_required
def editClient(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.name = request.form['name']
        client.address = request.form['address']
        client.phone = request.form['phone']
        client.email = request.form['email']
        client.contact_person = request.form['contact_person']
        client.contact_phone = request.form['contact_phone']
        client.contact_email = request.form['contact_email']
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('auth.editClient', id=id))
    return render_template('admin_edit/editClient.html', client=client)


@auth.route('/editProject/<int:id>', methods=['GET', 'POST'])
def editProject(id):
    project = Projects.query.get(id)
    clients = Client.query.all()

    if request.method == 'POST':
        project.name = request.form['name']
        project.project_description = request.form['project_description']
        project.date_commenced = request.form['date_commenced']
        project.date_completed = request.form['date_completed']
        project.isCompleted = True if 'isCompleted' in request.form else False
        project.client_id = request.form['client_id']
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('auth.editProject', id=id))
    return render_template('admin_edit/editProject.html', project=project, clients=clients)


@auth.route('/editApplicant/<int:id>', methods=['GET', 'POST'])
@login_required
def editApplicant(id):
    applicant = Applicant.query.get_or_404(id)
    if request.method == 'POST':
        user_id = request.form['user_id']
        job_id = request.form['job_id']
        date_submitted = request.form['date_submitted']
        status = request.form['status']
        resume = request.files['resume']
        cover_file = request.files['cover_file']
        applicant.user_id = user_id
        applicant.job_id = job_id
        applicant.date_submitted = date_submitted
        applicant.status = status
        if resume and allowed_file(resume.filename):
            resume_filename = secure_filename(resume.filename)
            resume_path = os.path.join(os.path.join("mainApp/static/files/resume", resume_filename))
            resume.save(resume_path)
            applicant.resume = resume_filename
        if cover_file and allowed_file(cover_file.filename):
            cover_filename = secure_filename(cover_file.filename)
            cover_file_path = os.path.join("mainApp/static/files/cover_file", cover_filename)
            cover_file.save(cover_file_path)
            applicant.cover_file = cover_filename
        db.session.commit()
        return redirect(url_for('auth.editApplicant', id=applicant.id))
    return render_template('admin_edit/editApplicant.html', applicant=applicant)


@auth.route('/editJob/<int:id>', methods=['GET', 'POST'])
@login_required
def editJob(id):
    job = Job.query.get_or_404(id)
    if request.method == 'POST':
        job.name = request.form['name']
        job.job_description = request.form['description']
        job.salary = request.form['salary']
        job.skills = request.form['skills']
        job.startApply = request.form['start_date']
        job.endApply = request.form['end_date']
        job.type = request.form['type']
        job.isAvailable = True if 'is_available' in request.form else False
        db.session.commit()
        flash('Job updated successfully', 'success')
        return redirect(url_for('auth.editJob', id=id))
    return render_template('admin_edit/editJob.html', job=job)


@auth.route('/showApplicants')
def showApplicants():
    applicants = Applicant.query.all()
    users = User.query.all()
    return render_template('admin/showApplicants.html', users=users, applicants=applicants)


@auth.route('/signup', methods=['GET', 'POST'])
# @cache.cached(timeout=60)
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('fname')
        lastName = request.form.get('lname')
        middleName = request.form.get('mname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        date_of_birth = request.form.get('dob')
        password = request.form.get('pass1')
        password1 = request.form.get('pass2')
        pic = request.files['pic']
        picname = secure_filename(pic.filename)
        pic_name = f'{str(uuid.uuid1())}_{email}_{picname}'

        if picname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.jfif')):
            pic.save(os.path.join("mainApp/static/profiles/", pic_name))
        else:
            flash('Please upload a picture', category='error')
            return render_template('signup.html', user=current_user)

        mpFace = mp.solutions.face_detection
        face = mpFace.FaceDetection(min_detection_confidence=0.9)
        frame = cv.imread(os.path.join("mainApp/static/profiles/", pic_name))
        gray = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = face.process(gray)
        if results.detections:
            pass
        else:
            flash('Please upload a picture of your face', category='error')
            return render_template('signup.html', user=current_user)

        admin_present = User.query.all()
        if not admin_present:
            superuser = True
        else:
            superuser = False

        user = User.query.filter_by(email=email.lower()).first()
        if user:
            flash('Email already exists', category='error')
            return render_template('signup.html', user=current_user)
        if len(password) < 7:
            flash('Password too short, must be at least 7 characters', category='error')
            return render_template('signup.html', user=current_user)
        if password1 != password:
            flash('Password mismatch', category='error')
            return render_template('signup.html', user=current_user)
        else:
            new_user = User(
                firstName=firstName.title(),
                middleName=middleName.title(),
                lastName=lastName.title(),
                phone=phone,
                img=pic_name,
                email=email.lower(),
                date_of_birth=date_of_birth,
                is_superuser=superuser,
                is_admin=superuser,
                password=generate_password_hash(password, method='sha256')
            )
            send_mail(new_user)
            Check = User.query.filter_by(email=email.lower()).first()
            if Check is None:
                os.remove(os.path.join("mainApp/static/profiles/", pic_name))
                flash('Form could not be processed please try again', category='error')
                return render_template('signup.html', user=current_user)
            if Check.email == email.lower():
                flash('Account created, an email has been sent to you.', category='success')
                return redirect(url_for("auth.login"))
            os.remove(os.path.join("mainApp/static/profiles/", pic_name))
            flash('Form could not be processed please try again', category='error')
    return render_template('signup.html', user=current_user)
