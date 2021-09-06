from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from django.shortcuts import render
import os
from datetime import datetime
import json
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import jsonify

'''
python3 app.py to run

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv activate New-Todo-App
'''
app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'test_log.log')

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    description = db.Column(db.String(150))
    start = db.Column(db.String(150))

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    start = StringField("Start Time", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/home")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)

@app.route("/")
def entry():
    return redirect(url_for("home"))

@app.route("/clear")
def clear():
    todo_list = Todo.query.all()
    todo_list[:] = []
    db.session.query(Todo).delete()
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    description = request.form.get("description")
    start = request.form.get("start")
    new_todo = Todo(name=name, complete=False, description=description, start=start)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    form = UserForm()
    name_to_update = Todo.query.get_or_404(todo_id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.description = request.form['description']
        name_to_update.start = request.form['start']
        try:
            db.session.commit()
            return render_template("edit.html", 
            form=form, 
            name_to_update=name_to_update)
        except:
            return render_template("edit.html", 
            form=form, 
            name_to_update=name_to_update)
    else:
        return render_template("edit.html", 
            form=form, 
            name_to_update=name_to_update)

class New_Todo(db.Model):
    new_id = db.Column(db.Integer, primary_key=True)
    new_name = db.Column(db.String(50))
    new_complete = db.Column(db.Boolean)
    new_description = db.Column(db.String(150))
    new_start = db.Column(db.String(150))

@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    return render_template("calendar.html")

@app.route('/calendar/<userInfo>/<daysInMonth>/<userMonth>', methods=['POST', 'GET'])
def calendarDay(userInfo, daysInMonth, userMonth):
    new_todo_list = New_Todo.query.all()

    daysInMonth = json.loads(daysInMonth)
    daysInMonth = int(daysInMonth)

    userInfo = json.loads(userInfo)
    userInfo = int(userInfo)

    userMonth = json.loads(userMonth)
    userMonth = int(userMonth)

    if userInfo > daysInMonth:
        return render_template("404.html")
    if userInfo < 1:
        return render_template("404.html")

    return render_template('calendarDay.html', new_todo_list=new_todo_list, daysInMonth=daysInMonth , userInfo=userInfo, userMonth=userMonth)


@app.route("/calendar/<userInfo>/<daysInMonth>/<userMonth>/clear")
def new_clear(userInfo, daysInMonth, userMonth):
    new_todo_list = New_Todo.query.all()
    new_todo_list[:] = []
    db.session.query(New_Todo).delete()
    db.session.commit()
    return redirect(url_for('calendarDay', userInfo=userInfo, daysInMonth=daysInMonth, userMonth=userMonth))

@app.route("/calendar/<userInfo>/<daysInMonth>/<userMonth>/add", methods=["POST"])
def new_add(userInfo, daysInMonth, userMonth):
    new_name = request.form.get("new_name")
    new_description = request.form.get("new_description")
    new_start = request.form.get("new_start")
    new_new_todo = New_Todo(new_name=new_name, new_complete=False, new_description=new_description, new_start=new_start)
    db.session.add(new_new_todo)
    db.session.commit()
    return redirect(url_for('calendarDay', userInfo=userInfo, daysInMonth=daysInMonth, userMonth=userMonth))

@app.route("/calendar/<userInfo>/<daysInMonth>/<userMonth>/update/<int:new_id>")
def new_update(new_id, userInfo, daysInMonth, userMonth):
    new_todo = New_Todo.query.filter_by(new_id=new_id).first()
    new_todo.new_complete = not new_todo.new_complete
    db.session.commit()
    return redirect(url_for('calendarDay', userInfo=userInfo, daysInMonth=daysInMonth, userMonth=userMonth))

@app.route("/calendar/<userInfo>/<daysInMonth>/<userMonth>/delete/<int:new_id>")
def new_delete(new_id, userInfo, daysInMonth, userMonth):
    new_todo = New_Todo.query.filter_by(new_id=new_id).first()
    db.session.delete(new_todo)
    db.session.commit()
    return redirect(url_for('calendarDay', userInfo=userInfo, daysInMonth=daysInMonth, userMonth=userMonth))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000)))