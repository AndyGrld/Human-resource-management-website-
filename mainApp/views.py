from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from email.mime.multipart import MIMEMultipart
from mainApp.auth import epassword, me
from email.mime.text import MIMEText
from mainApp import db
import datetime
import smtplib

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html', user=current_user)
