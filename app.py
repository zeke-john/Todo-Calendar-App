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
from webforms import *
from flask_ckeditor import CKEditor
from wtforms.widgets import TextArea   
from wtforms import StringField, SubmitField, PasswordField, ValidationError, TimeField, SelectMultipleField
import re
from lxml import html
import ast

app = Flask(__name__)
ckeditor = CKEditor(app)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'test_log.log')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:CAez0208@localhost/todoapp?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = '\xa1\x84\xce\xd8\xe8\xf2Z\xdfz\xa3p\x95S\x1e@9J\xa0R\xa4"\xca={'

login_manager = LoginManager()
login_manager.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zekejohn118@gmail.com'
app.config['MAIL_PASSWORD'] = 'CAez0208'
mail = Mail(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class Labels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(4294967295), nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    complete = db.Column(db.Boolean)
    description = db.Column(db.String(150), nullable=False)
    start = db.Column(db.String(150))
    date = db.Column(db.String(150), nullable=False)
    day = db.Column(db.String(150), nullable=False)
    month = db.Column(db.String(150), nullable=False)
    year = db.Column(db.String(150), nullable=False)
    labels = db.Column(db.String(200))
    #create forenign key to link users to tasks
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Notes(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(65535635655))
    description = db.Column(db.Text(6553563565))
    #create forenign key to link users to tasks
    poster_notes_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    password_hash = db.Column(db.String(128))
    password_hash2 = db.Column(db.String(128))
    posts = db.relationship('Todo', backref="poster")
    post_notes = db.relationship('Notes', backref="poster_notes")

    def get_reset_token(self, expires_sec=300):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password) 

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signUp", methods=["GET", "POST"])
def signUp():
    form = Sign_up_Form()
    if form.password_hash.data != form.password_hash2.data:
        flash("Passwords Must Match!") 
    try:
        if len(form.password_hash.data) < 8:
            flash("Passwords must be at least 8 charectars long!")
    except TypeError:
        pass
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Great! Now just Login and your Ready to Go!")
        elif user is not None:
            flash("That Email is already being used...")
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
    return render_template("signUp.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                return redirect(url_for("today", user_id=current_user.id))
            else:
                flash("Incorrect Email or Password")
        else:   
            flash("Incorrect Email or Password")
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been Logged out, Thanks for stopping by!")
    return redirect(url_for('login'))

@app.route("/userInfo", methods=["GET", "POST"])
@login_required
def userInfo():
    return render_template("userInfo.html")

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="zekejohn118@gmail.com", recipients=[user.email])

    msg.body = f'''To reset your Password for Todo App, visit the link to do so. It will expire in 5 minutes: {url_for('reset_token', token=token, _external = True)}
    

    If you didn't make this request then ignore this email
    '''
    mail.send(msg)

class RequestResetForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Next")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            flash('If an account with this email address exists, a password reset message will be sent shortly.')
            raise ValidationError('If an account with this email address exists, a password reset message will be sent shortly.')

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        flash("If an account with this email exists, a password reset message will be sent shortly.")
        send_reset_email(user)
    return render_template('reset_request.html', form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    user = Users.verify_reset_token(token)
    if user is None: 
        flash("invalid or expired token")
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.password_hash.data != form.password_hash2.data:
        flash("Passwords Must Match!")
    try:
        if len(form.password_hash.data) < 8:
            flash("Passwords Must be at least 8 charectars long!")
    except TypeError:
        pass
    if form.validate_on_submit():
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user.password_hash = hashed_pw
            db.session.commit()
            flash("Your password has been updated, now you can login")
    return render_template("reset_password.html", form=form)

@app.route("/labels/<int:id>" , methods=["POST", "GET"])
@login_required
def labels(id):
    form = AddLabelForm()
    if id != current_user.id:
        return redirect(url_for('login'))
    labels_list = Labels.query.all()
    return render_template("labels.html", form=form, labels_list=labels_list)


@app.route("/delete/label/<int:label_id>")
@login_required
def delete_label(label_id):
    post_to_delete = Labels.query.get_or_404(label_id)
    label = Labels.query.filter_by(id=label_id).first()
    db.session.delete(label)
    db.session.commit()
    return redirect(url_for("labels", id=current_user.id))

@app.route("/labels/add" , methods=["POST"])
@login_required
def labels_add():
    form = AddLabelForm()
    if request.method == "POST":
        try:
            if form.name.data.isspace():
                flash("Please enter a valid name")
                return redirect(url_for('labels', form=form, id=current_user.id))
            if '[' in form.name.data:
                flash("Please enter a valid name")
                return redirect(url_for('labels', form=form, id=current_user.id))
            if ']' in form.name.data:
                flash("Please enter a valid name")
                return redirect(url_for('labels', form=form, id=current_user.id))
            if ',' in form.name.data:
                flash("Please enter a valid name")
                return redirect(url_for('labels', form=form, id=current_user.id))
            else:
                form.name.data =  form.name.data.replace(" ", "_")
                new_label = Labels(name=form.name.data)
                db.session.add(new_label)
                db.session.commit()
                return redirect(url_for('labels', form=form, id=current_user.id))
        except:
            flash("There was an error when making your label, Try again")
            return redirect(url_for("labels", form=form, id=current_user.id))
    else:
        flash("There was an error when making your label, Try again")
        return redirect(url_for("labels", form=form, id=current_user.id))

@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
@login_required
def edit_task(todo_id):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        form = EditForm()
        name_to_update = Todo.query.get_or_404(todo_id)
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.description = request.form['description']
            name_to_update.start = request.form['start']
            try:
                db.session.commit()
                flash("Task Updated")
                return render_template("editTask.html", 
                form=form, 
                name_to_update=name_to_update)
            except:
                flash("Error!  Looks like there was a problem... Try again!")
                return render_template("editTask.html", 
                form=form, 
                name_to_update=name_to_update)
        else:
            return render_template("editTask.html", 
                form=form, 
                name_to_update=name_to_update)
    else:
        return redirect(url_for("today"))


@app.route("/labels/view/<int:labels_id>" , methods=["POST", "GET"])
@login_required
def labels_view(labels_id):
    label_to_see = Labels.query.get_or_404(labels_id)
    form = AddLabelForm()
    todoist = Todo.query.all()
    todo_list = Todo.query.filter_by(labels=label_to_see.id).all()
    for todos in todoist:
        todos.labels = todos.labels.split(',')
        todos.labels=todos.labels
        for todos.labels in todos.labels:
            if str(todos.labels) == str(label_to_see.id):
                todo_list = Todo.query.filter_by(labels=label_to_see.id).all()
                return render_template("labelsView.html", form=form, labelname=label_to_see, todo_list=todo_list)
    return render_template("labelsView.html", form=form, labelname=label_to_see, todo_list=todo_list)


@app.route("/today")
@login_required
def today():
    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day
    curr_date = f"{curr_month} {curr_day} {curr_year}"
    home_todo_list = Todo.query.filter_by(date=curr_date).all() #where date = to the present
    labels_list = Labels.query.all()
    return render_template("today.html", home_todo_list=home_todo_list, labels_list=labels_list)


@app.route("/add", methods=["POST"] )
@login_required
def add():  
    name = request.form['name']
    description = request.form['description']
    time = request.form['time']
    taskdate = request.form['taskdate']
    tasklabels = request.form['tasklabels']
    if name and taskdate:
        punctuation='!?,.:;"\')(_-'
        new_day ='' # Creating empty string
        for i in str(taskdate):
            if(i not in punctuation):
                        new_day += i
        new_day = new_day.split()
        print(new_day)
        month = new_day[0]
        day = new_day[1]
        year = new_day[-1]
        date = f'{month} {day} {year}'
        new_todo = Todo(name=name, complete=False, description=description, start=time, date=date, month=month, day=day, year=year, poster_id=current_user.id, labels=tasklabels)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'name' : 'Task Added'})

    return jsonify({'error' : 'Please fill out the name and date of your task'})

@app.route("/notes/<int:id>" , methods=["POST", "GET"])
@login_required
def notes(id):
    if id != current_user.id:
        return redirect(url_for('login'))
    class addNotes(FlaskForm):
        notes_list = Notes.query.filter_by(poster_notes_id=current_user.id).all()
        if notes_list != []:
            for notes in notes_list:
                name = StringField("Name",  default=notes.name)
                description = StringField("Description", widget=TextArea(),  default=notes.description)
                submit = SubmitField("Save")
        else:
            description = 'do something!'
            name = 'Notes'
            name = StringField("Name",  default=name)
            description = StringField("Description", widget=TextArea(),  default=description)
            submit = SubmitField("Save")
    form = addNotes()
    return render_template("notes.html", form=form)

class addNotes(FlaskForm):
    notes_list = Notes.query.all()
    if notes_list != []:
        for notes in notes_list:
            description = notes.description
            name = notes.name
            name = StringField("Name",  default=notes.name)
            description = StringField("Description", widget=TextArea(),  default=notes.description)
            submit = SubmitField("Save")
    else:
        description = 'do something!'
        name = 'Notes'
        name = StringField("Name",  default=name)
        description = StringField("Description", widget=TextArea(),  default=description)
        submit = SubmitField("Save")

@app.route("/notes/add" , methods=["POST", "GET"])
@login_required
def notesAdd():
    form = addNotes()   
    if request.method == "POST":
        try:
            notes_list = Notes.query.all()
            if notes_list == []:
                poster_notes = current_user.id
                new_note = Notes(name=form.name.data, description=form.description.data, poster_notes_id=poster_notes)
                notes = Notes.query.first()
                db.session.add(new_note)
                try:
                    db.session.commit()
                    flash("Note Saved")
                    return redirect(url_for("notes", form=form, id=current_user.id, name=form.name.data, description=form.description.data))
                except:
                    db.session.rollback()
                    flash("There was an error when saving your note, Try again")
                    return redirect(url_for("notes", form=form, id=current_user.id))
            else:
                notes = Notes.query.first()
                notes.name = form.name.data
                notes.description = form.description.data
                poster_notes = current_user.id
                new_note = Notes(name=notes.name, description=notes.description, poster_notes_id=poster_notes)   
                db.session.add(new_note)
                try:
                    db.session.commit()
                    flash("Note Saved")
                    return redirect(url_for("notes", form=form, id=current_user.id, name=form.name.data, description=form.description.data))
                except:
                    db.session.rollback()
                    flash("There was an error when saving your note, Try again")
                    return redirect(url_for("notes", form=form, id=current_user.id))
        except:
            flash("There was an error when saving your note, Try again")
            return redirect(url_for("notes", form=form, id=current_user.id))
    else:
        flash("There was an error when saving your note, Try again")
        return redirect(url_for("notes", form=form, id=current_user.id))

@app.route('/updateUser/<int:id>', methods=['GET', 'POST'])
@login_required
def editUser(id):
    if id != current_user.id:
        return redirect(url_for('login'))
    else:
        form = UserEditForm()
        name_to_update = Users.query.get_or_404(id)
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            try:
                db.session.commit()
                flash("Account Info Updated")
                return render_template("editUser.html", 
                    form=form,
                    name_to_update = name_to_update, id=id)
            except:
                flash("Error!  Looks like there was a problem... Try again!")
                return render_template("editUser.html", 
                    form=form,
                    name_to_update = name_to_update,
                    id=id)
        else:
            return render_template("editUser.html", 
                    form=form,
                    name_to_update = name_to_update,
                    id = id)

@app.route("/calendar", methods=["GET", "POST"])
@login_required
def calendar():
    # need to get all the tasks for each individul day when loaded, most likly by seeing the date they picked when adding task
    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day
    curr_date = f"{curr_month} {curr_day} {curr_year}"
    if Todo.date != curr_date:
        date_of_todo = []
        calendar_todo_list = Todo.query.filter(Todo.date != curr_date).all()
        for todos in calendar_todo_list:
            if todos.poster_id == current_user.id:
                if str(todos.complete) == 'False':
                    date_of_todo.append(todos.date)
                    date_of_todo = date_of_todo
                if str(todos.complete) == 'True':
                    comp_date = todos.date + "s" #to diffrentioat between the cmpleted and not
                    date_of_todo.append(comp_date)
                    date_of_todo = date_of_todo
    return render_template("calendar.html", date_of_todo=date_of_todo)      

@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>', methods=['POST', 'GET'])
@login_required
def calendarDay(day_hover, monthuser, yearuser):
    
    curr_month = datetime.date.today().strftime("%B")
    monthuser = curr_month
    day_hover = json.loads(day_hover)
    day_hover = day_hover
    yearuser = json.loads(yearuser)
    date_user = f"{monthuser} {day_hover} {yearuser}"  

    calendar_todo_list = Todo.query.filter(Todo.date.endswith(date_user)).all()
    labels_list = Labels.query.all()
    return render_template('calendarDay.html', monthuser=monthuser , calendar_todo_list=calendar_todo_list, day_hover=day_hover, yearuser=yearuser,labels_list=labels_list)


@app.route('/deleteUser/<int:id>')
@login_required
def deleteUser(id):
    if id != current_user.id:
        return redirect(url_for('login'))
    else:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = Sign_up_Form()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Account Deleted")

            return render_template("signUp.html", 
            form=form,
            name=name)

        except:
            flash("Whoops! There was a problem deleting user, try again...")
            return render_template("signUp.html", 
            form=form, name=name)

def send_change_email(user):
    token = user.get_reset_token()
    msg = Message('Password Change Request', sender="zekejohn118@gmail.com", recipients=[user.email])

    msg.body = f'''To Change your Password for Todo App, visit the link below. It will expire in 5 minutes:
    {url_for('change_token', token=token, _external = True)}
    

    If you didn't make this request then ignore this email
    '''
    mail.send(msg)

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_request():
    user = user = Users.query.filter_by(email=current_user.email).first()
    send_change_email(user)
    flash("An email has been sent to you to change your password.")
    return redirect(url_for('editUser', id=current_user.id))    

@app.route("/change_password/<token>", methods=["GET", "POST"])
@login_required
def change_token(token):
    user = Users.verify_reset_token(token)
    if user is None: 
        flash("invalid or expired token")
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.password_hash.data != form.password_hash2.data:
        flash("Passwords Must Match!")
    try:
        if len(form.password_hash.data) < 8:
            flash("Passwords Must be at least 8 charectars long!")
    except TypeError:
        pass
    if form.validate_on_submit():
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user.password_hash = hashed_pw
            db.session.commit()
            flash("Your password has been updated, now you can login")
    return render_template("reset_password.html", form=form)


@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>/update/<int:todo_id>', methods=['POST', 'GET'])
@login_required
def update_cal(todo_id, day_hover, monthuser, yearuser):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        curr_month = datetime.date.today().strftime("%B")
        day_hover = json.loads(day_hover)
        monthuser = curr_month
        yearuser = json.loads(yearuser)

        todo = Todo.query.filter_by(id=todo_id).first()
        todo.complete = not todo.complete
        db.session.commit()
        return redirect(url_for("calendarDay", yearuser=yearuser, monthuser=monthuser, day_hover=day_hover, todo_id=todo_id ))
    else:
        return redirect(url_for("today"))

@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>/delete/<int:todo_id>', methods=['POST', 'GET'])
@login_required
def delete_cal(todo_id, day_hover, monthuser, yearuser):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        curr_month = datetime.date.today().strftime("%B")
        day_hover = json.loads(day_hover)
        monthuser = curr_month
        yearuser = json.loads(yearuser)

        todo = Todo.query.filter_by(id=todo_id).first()
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("calendarDay", yearuser=yearuser, monthuser=monthuser, day_hover=day_hover, todo_id=todo_id ))
    else:
        return redirect(url_for("today"))

@app.route("/calendar/<day_hover>/<monthuser>/<yearuser>/edit/<int:todo_id>", methods=["GET", "POST"])
@login_required
def edit_cal(todo_id, day_hover, monthuser, yearuser ):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        curr_month = datetime.date.today().strftime("%B")
        day_hover = json.loads(day_hover)
        monthuser = curr_month
        yearuser = json.loads(yearuser)
        form = EditForm()
        name_to_update = Todo.query.get_or_404(todo_id)
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.description = request.form['description']
            name_to_update.start = request.form['start']
            try:
                db.session.commit()
                flash("Task Updated")
                return render_template("editCal.html", 
                form=form, 
                name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)
            except:
                flash("Error!  Looks like there was a problem... Try again!")
                return render_template("editCal.html", 
                form=form, 
                name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)
        else:
            return render_template("editCal.html", 
                form=form, 
                name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)
    else:
        return redirect(url_for("today"))

@app.route("/update/<int:todo_id>")
@login_required
def update_task(todo_id):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.complete = not todo.complete
        db.session.commit()
        return redirect(url_for("today"))
    else:
        return redirect(url_for("today"))

@app.route("/delete/<int:todo_id>")
@login_required
def delete_task(todo_id):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        todo = Todo.query.filter_by(id=todo_id).first()
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("today"))
    else:
        return redirect(url_for('today'))


@app.route("/labels/view/update/<int:todo_id>")
@login_required
def update_task_labels(todo_id):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.complete = not todo.complete
        db.session.commit()
        return redirect(url_for("labels_view"))
    else:
        return redirect(url_for("labels_view"))

@app.route("/labels/view/delete/<int:todo_id>")
@login_required
def delete_task_labels(todo_id):
    post_to_delete = Todo.query.get_or_404(todo_id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        todo = Todo.query.filter_by(id=todo_id).first()
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("labels_view"))
    else:
        return redirect(url_for('labels_view'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

@app.errorhandler(401)
def page_not_found(e):
    return render_template("401.html")

@app.errorhandler(400)
def page_not_found(e):
    return render_template("400.html")

@app.errorhandler(403)
def page_not_found(e):
    return render_template("403.html")

@app.errorhandler(403)
def page_not_found(e):
    return render_template("403.html")

@app.errorhandler(408)
def page_not_found(e):
    return render_template("408.html")

@app.errorhandler(501)
def page_not_found(e):
    return render_template("501.html")

@app.errorhandler(502)
def page_not_found(e):
    return render_template("502.html")

@app.errorhandler(503)
def page_not_found(e):
    return render_template("503.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000)))