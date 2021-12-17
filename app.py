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

app = Flask(__name__)
ckeditor = CKEditor(app)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'test_log.log')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:CAez0208@localhost/users?charset=utf8mb4'
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
    #create forenign key to link users to tasks
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(1900))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    password_hash = db.Column(db.String(128))
    password_hash2 = db.Column(db.String(128))
    posts = db.relationship('Todo', backref="poster")

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
        if len(form.password_hash.data) < 10:
            flash("Passwords must be at least 10 charectars long!")
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


@app.route("/today")
@login_required
def today():
    form = addtaskForm() 
    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day
    
    curr_date = f"{curr_month} {curr_day} {curr_year}"
    home_todo_list = Todo.query.filter_by(date=curr_date).all() #where date = to the present
    return render_template("today.html", home_todo_list=home_todo_list, form=form)


@app.route("/add", methods=["POST"] )
@login_required
def add():  
    form = addtaskForm() 
    if request.method == "POST":
        try:
            punctuation='!?,.:;"\')(_-'
            new_day ='' # Creating empty string
            for i in form.date.data:
                if(i not in punctuation):
                            new_day += i
            new_day = new_day.split()

            month = new_day[0]
            day = new_day[1]
            year = new_day[-1]
            date = f'{month} {day} {year}'
            new_todo = Todo(name=form.name.data, complete=False, description=form.description.data, start=form.time.data, date=date, month=month, day=day, year=year, poster_id=current_user.id)

            curr_month = datetime.date.today().strftime("%B")
            curr_year = datetime.date.today().strftime("%Y")
            now = datetime.datetime.now()
            curr_day = now.day

            curr_date = f"{curr_month} {curr_day} {curr_year}"
            if date != curr_date:
                flash(f'Task Added')
            db.session.add(new_todo)
            db.session.commit()
            return redirect(url_for("today", form=form))
        except:
            flash('There was an error when adding your task, Try again')
            return redirect(url_for("today", form=form))
    else:
        flash('There was an error when adding your task, Try again')
        return redirect(url_for("today", form=form))

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
                flash("Task Updated Successfully")
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
                flash("Account Info Updated Successfully")
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

    return render_template('calendarDay.html', monthuser=monthuser , calendar_todo_list=calendar_todo_list, day_hover=day_hover, yearuser=yearuser)


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
            flash("Account Deleted Successfully")

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
        if len(form.password_hash.data) < 10:
            flash("Passwords Must be at least 10 charectars long!")
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
                flash("Task Updated Successfully")
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