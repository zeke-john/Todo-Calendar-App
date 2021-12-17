from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from django.shortcuts import render
import os
import datetime
import json
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, TimeField
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
from wtforms.widgets import TextArea   
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
SHOW COLUMNS FROM table_name IN database_name;
______________________________________
MEMES FOR DA BOIS
Why can't python functions hear? Because they're def
What's the 2nd movie about a database engineer called? The SQL
What’s the object-oriented way to become wealthy? Inheritance 
Why did the programmer quit his job? Because he didn't get arrays.
I would've liked to tell you an infinite loop joke but I'm afraid you'll never hear the end of it
Why did MongoDB eat alone? Because it didn’t know how to join tables
Why was the Linux user’s house so hot in the summer? Cause he didn't have Windows.
Why do programmers prefer dark mode? Because light attracts bugs.
What did True say to False? Stop boolean me
'''

class EditForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    start = StringField("Start Time")
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
    time = StringField("Start Time")
    date = StringField("Date", validators=[DataRequired()])
    submit = SubmitField("Add Task")

class addNotes(FlaskForm):
    name = StringField("Name")
    description = StringField("Description", widget=TextArea())
    submit = SubmitField("Save")