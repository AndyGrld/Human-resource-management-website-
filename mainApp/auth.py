from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from .models import User, Employee, Client, Projects, Job, Applicant
from email.mime.text import MIMEText
from mainApp.models import User
from . import db, cache
import uuid as uuid
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
    message['subject'] = "Welcome"
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
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    return render_template('admin/admin.html', now=current_user, users=User.query.all(), projects=Projects.query.all(),
                           jobs = Job.query.all(), available_jobs = Job.query.filter_by(isAvailable=True).all(),
                           employees=Employee.query.all(), clients=Client.query.all(),
                           applicants=Applicant.query.all(),
                           completed_projects = Projects.query.filter_by(isCompleted=True).all())


@login_required
@auth.route('/showEmployees')
def showEmployees():
    if not current_user.is_admin:
        return "Page not found"
    employees = Employee.query.all()
    return render_template('admin/showEmployees.html', employees=employees)


@login_required
@auth.route('/showClients')
def showClients():
    if not current_user.is_admin:
        return "Page not found"
    clients = Client.query.all()
    return render_template('admin/showClients.html', clients=clients)


@login_required
@auth.route('/showProjects')
def showProjects():
    if not current_user.is_admin:
        return "Page not found"
    projects = Projects.query.all()
    return render_template('admin/showProjects.html', projects=projects)


@login_required
@auth.route('/showJobs')
def showJobs():
    if not current_user.is_admin:
        return "Page not found"
    jobs = Job.query.all()
    return render_template('admin/showJobs.html', jobs=jobs)


@login_required
@auth.route('/showUsers')
def showUsers():
    if not current_user.is_admin:
        return "Page not found"
    users = User.query.all()
    others = User.query.filter_by(EMPLOYEE = None).all()
    return render_template('admin/showUsers.html', users=users, others=others)


@login_required
@auth.route('/editUser/<int:id>', methods=['GET', 'POST'])
@login_required
def editUser(id):
    if not current_user.is_admin:
        return "Page not found"
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.firstName = request.form['firstName']
        user.middleName = request.form['middleName']
        user.lastName = request.form['lastName']
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        user.img = request.form['img']
        user.is_superuser = True if request.form.get('is_superuser') else False
        user.is_admin = True if request.form.get('is_admin') else False
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully', 'success')
    return render_template('admin_edit/editUser.html', user=user)


@login_required
@auth.route('/admin/addUser', methods=['GET', 'POST'])
def addUser():
    if not current_user.is_admin:
        return "Page not found"
    if request.method == 'POST':
        firstName = request.form['firstName']
        middleName = request.form['middleName']
        lastName = request.form['lastName']
        phone = request.form['phone']
        email = request.form['email']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        pic = request.form['img']
        picname = secure_filename(pic.filename)
        pic_name = f'{str(uuid.uuid1())}_{email}_{picname}'
        is_superuser = True if request.form.get('is_superuser') else False
        is_admin = True if request.form.get('is_admin') else False
        password = generate_password_hash(request.form['password'])
        new_user = User(
            firstName=firstName.title(),
            middleName=middleName.title(),
            lastName=lastName.title(),
            phone=phone,
            img=pic_name,
            email=email.lower(),
            date_of_birth=date_of_birth,
            is_superuser=is_superuser,
            is_admin=is_admin,
            password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully', 'success')
        return redirect(url_for('auth.addUser'))
    return render_template('admin_add/addUser.html')


@auth.route('/editEmployee/<int:id>', methods=['GET', 'POST'])
@login_required
def editEmployee(id):
    if not current_user.is_admin:
        return "Page not found"
    jobs = Job.query.all()
    employee = Employee.query.get_or_404(id)
    projects = Projects.query.all()
    user = employee.user
    if request.method == 'POST':
        user.firstName = request.form['firstName']
        user.middleName = request.form['middleName']
        user.lastName = request.form['lastName']
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        user.img = request.form['img']
        user.is_superuser = True if request.form.get('is_superuser') else False
        user.is_admin = True if request.form.get('is_admin') else False
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
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
    return render_template('admin_edit/editEmployee.html', employee=employee, projects=projects, user=user, jobs=jobs)


@auth.route('/admin/addEmployee', methods=['GET', 'POST'])
@login_required
def addEmployee():
    if not current_user.is_admin:
        return "Page not found"
    if request.method == 'POST':
        user_id = request.form['user_id']
        if not user_id:
            flash("Could not find user id", category='error')
            return redirect(url_for('auth.addEmployee'))
        job_id = request.form['job_id']
        about = request.form['about']
        skills = request.form['skills']
        performance = request.form['performance']
        work_email = request.form['work_email']
        isManager = True if request.form.get('isManager') else False
        manager_id = request.form['manager_id']
        PROJECT = [Projects.query.get(project_id) for project_id in request.form.getlist('PROJECT')]
        new_employee = Employee(
            user_id=user_id,
            job_id=job_id,
            date_employed=datetime.today(),
            about=about,
            skills=skills,
            performance=performance,
            work_email=work_email,
            isManager=isManager,
            manager_id=manager_id,
            PROJECT=PROJECT,
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully.', 'success')
        return redirect(url_for('auth.addEmployee'))
    return render_template('admin_add/addEmployee.html', employees=Employee.query.all(),
                           projects=Projects.query.all(), users=User.query.all(), jobs=Job.query.all())


@auth.route('/editClient/<int:id>', methods=['GET', 'POST'])
@login_required
def editClient(id):
    if not current_user.is_admin:
        return "Page not found"
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.name = request.form['name']
        client.address = request.form['address']
        client.phone = request.form['phone']
        client.email = request.form['email']
        client.contact_person = request.form['contact_person']
        client.contact_email = request.form['contact_email']
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('auth.editClient', id=id))
    return render_template('admin_edit/editClient.html', client=client)


@auth.route('/admin/addClient', methods=['GET', 'POST'])
@login_required
def addClient():
    if not current_user.is_admin:
        return "Page not found"
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        contact_person = request.form['contact_person']
        contact_email = request.form['contact_email']
        new_client = Client(
            name=name,
            address=address,
            phone=phone,
            email=email,
            contact_person=contact_person,
            contact_email=contact_email
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully', 'success')
        return redirect(url_for('auth.addClient'))
    return render_template('admin_add/addClient.html')


@login_required
@auth.route('/editProject/<int:id>', methods=['GET', 'POST'])
def editProject(id):
    if not current_user.is_admin:
        return "Page not found"
    project = Projects.query.get(id)
    clients = Client.query.all()
    if request.method == 'POST':
        project.name = request.form['name']
        project.project_description = request.form['project_description']
        project.date_commenced = datetime.strptime(request.form['date_commenced'], '%Y-%m-%d').date()
        if request.form['date_completed']:
            project.date_completed = datetime.strptime(request.form['date_completed'], '%Y-%m-%d').date()
        project.isCompleted = True if 'isCompleted' in request.form else False
        project.client_id = request.form['client_id']
        db.session.commit()
        flash('Project updated successfully', 'success')
        return redirect(url_for('auth.editProject', id=id))
    return render_template('admin_edit/editProject.html', project=project, clients=clients)


@login_required
@auth.route('/admin/addProject', methods=['GET', 'POST'])
def addProject():
    if not current_user.is_admin:
        return "Page not found"
    clients = Client.query.all()
    if request.method == 'POST':
        name = request.form['name']
        project_description = request.form['project_description']
        date_commenced = datetime.strptime(request.form['date_commenced'], '%Y-%m-%d').date()
        client_name = request.form['client_name']
        client_id = Client.query.filter_by(name=client_name).first().id
        new_project = Projects(
            name=name,
            project_description=project_description,
            date_commenced=date_commenced,
            client_id=client_id,
        )
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully', 'success')
        return redirect(url_for('auth.addProject', id=id))
    return render_template('admin_add/addProject.html', clients=clients)


@auth.route('/editApplicant/<int:id>', methods=['GET', 'POST'])
@login_required
def editApplicant(id):
    if not current_user.is_admin:
        return "Page not found"
    applicant = Applicant.query.get_or_404(id)
    jobs = Job.query.all()
    if request.method == 'POST':
        user_id = request.form['user_id']
        job_id = request.form['job_id']
        date_submitted = datetime.strptime(request.form['date_submitted'], '%Y-%m-%d').date()
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
        flash('Applicant updated successfully', 'success')
        return redirect(url_for('auth.editApplicant', id=applicant.id))
    return render_template('admin_edit/editApplicant.html', applicant=applicant, jobs=jobs)


@auth.route('/editJob/<int:id>', methods=['GET', 'POST'])
@login_required
def editJob(id):
    if not current_user.is_admin:
        return "Page not found"
    job = Job.query.get_or_404(id)
    if request.method == 'POST':
        job.name = request.form['name']
        job.job_description = request.form['description']
        job.salary = request.form['salary']
        job.skills = request.form['skills']
        job.startApply = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        job.endApply = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        job.type = request.form['type']
        job.isAvailable = True if 'is_available' in request.form else False
        db.session.commit()
        flash('Job updated successfully', 'success')
        return redirect(url_for('auth.editJob', id=id))
    return render_template('admin_edit/editJob.html', job=job)


@auth.route('/admin/addJob', methods=['GET', 'POST'])
@login_required
def addJob():
    if not current_user.is_admin:
        return "Page not found"
    if request.method == 'POST':
        name = request.form['name']
        job_description = request.form['description']
        salary = request.form['salary']
        skills = request.form['skills']
        startApply = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        endApply = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        type = request.form['type']
        isAvailable = True if 'is_available' in request.form else False
        new_job = Job(
            name=name,
            job_description=job_description,
            salary=salary,
            skills=skills,
            startApply=startApply,
            endApply=endApply,
            type=type,
            isAvailable=isAvailable
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job added successfully', 'success')
        return redirect(url_for('auth.addJob', id=id))
    return render_template('admin_add/addJob.html')


@login_required
@auth.route('/showApplicants')
def showApplicants():
    if not current_user.is_admin:
        return "Page not found"
    applicants = Applicant.query.all()
    users = User.query.all()
    return render_template('admin/showApplicants.html', users=users, applicants=applicants)


@login_required
@auth.route('/admin/deleteUser/<int:id>')
def deleteUser(id):
    if not current_user.is_admin:
        return "Page not found"
    user = User.query.filter_by(id=id).first()
    os.remove(os.path.join('static/profiles',user.img))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted", category='success')
    return redirect(url_for("auth.showUsers"))


@auth.route('/admin/deleteEmployee/<int:id>')
@login_required
def deleteEmployee(id):
    if not current_user.is_admin:
        return "Page not found"
    employee = Employee.query.filter_by(id=id).first()
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted", category='success')
    return redirect(url_for("auth.showEmployees"))


@auth.route('/admin/deleteJob/<int:id>')
@login_required
def deleteJob(id):
    if not current_user.is_admin:
        return "Page not found"
    job = Job.query.filter_by(id=id).first()
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted", category='success')
    return redirect(url_for("auth.showJobs"))


@auth.route('/admin/deleteClient/<int:id>')
@login_required
def deleteClient(id):
    if not current_user.is_admin:
        return "Page not found"
    client = Client.query.filter_by(id=id).first()
    db.session.delete(client)
    db.session.commit()
    flash("Client deleted", category='success')
    return redirect(url_for("auth.showClients"))


@auth.route('/admin/deleteProject/<int:id>')
@login_required
def deleteProject(id):
    if not current_user.is_admin:
        return "Page not found"
    project = Projects.query.filter_by(id=id).first()
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted", category='success')
    return redirect(url_for("auth.showProjects"))


@auth.route('/admin/deleteApplicant/<int:id>')
@login_required
def deleteApplicant(id):
    if not current_user.is_admin:
        return "Page not found"
    applicant = Applicant.query.filter_by(id=id).first()
    os.remove(os.path.join('mainApp/static/files/cover_file', applicant.cover_file))
    os.remove(os.path.join('mainApp/static/files/resume', applicant.resume))
    db.session.delete(applicant)
    db.session.commit()
    flash("Applicant deleted", category='success')
    return redirect(url_for("auth.showApplicants"))


@auth.route('/signup', methods=['GET', 'POST'])
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

        if picname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.jfif')):
            pic.save(os.path.join("mainApp/static/profiles/", pic_name))
        else:
            flash('Please upload a picture', category='error')
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
                os.remove(os.path.join("static/profiles/", pic_name))
                flash('Form could not be processed please try again', category='error')
                return render_template('signup.html', user=current_user)
            if Check.email == email.lower():
                flash('Account created, an email has been sent to you.', category='success')
                return redirect(url_for("auth.login"))
            os.remove(os.path.join("static/profiles/", pic_name))
            flash('Form could not be processed please try again', category='error')
    return render_template('signup.html', user=current_user)
