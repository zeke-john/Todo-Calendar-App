from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from django.shortcuts import render
import os
import datetime
import json
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask import jsonify
import calendar as cal
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.html5 import EmailField 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from flask_migrate import Migrate
from app import Users
from wtforms.widgets import  TextArea
'''
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate New-Todo-App
python3 app.py to run              
______________________________________
python3 -m flask db 
python3 -m flask db migrate -m 'message'
python3 -m flask db upgrade
______________________________________
export PATH=$PATH:/usr/local/mysql/bin/
sudo mysql -u root -p
USE users;
SHOW TABLES;
SELECT * FROM [table name];
'''

class EditForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    start = StringField("Start Time", validators=[DataRequired()])
    submit = SubmitField("Save")

class Sign_up_Form(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='passwords must match'), Length(min=8)])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class UserEditForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = EmailField("Email", validators=[DataRequired(), Email()])
	submit = SubmitField("Save Changes")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")

class ResetPasswordForm(FlaskForm):
    password_hash = PasswordField("New Password", validators=[DataRequired(), EqualTo('password_hash2', message='passwords must match'), Length(min=8)])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class RequestResetForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Next")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            flash('If an account with this email address exists, a password reset message will be sent shortly.')
            raise ValidationError('If an account with this email address exists, a password reset message will be sent shortly.')

class addtaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    time = StringField("Start Time", validators=[DataRequired()])
    date = StringField("Date", validators=[DataRequired()])
    submit = SubmitField("Add Task")