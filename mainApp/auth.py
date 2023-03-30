from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
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
    return render_template('admin.html', now=current_user, users=User.query.all())


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
