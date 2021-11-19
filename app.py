from typing import NoReturn
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from django.shortcuts import render
import os
import datetime
import json
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import jsonify
import calendar as cal
'''
python3 app.py to run

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv activate New-Todo-App

sqlite3
sqlite> .open "db.sqlite"
sqlite> .databases
sqlite> .tables
sqlite> .headers on
sqlite> .mode column
SELECT * FROM todo;
SELECT * FROM todo WHERE __ = '_';

'''
app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'test_log.log')

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(999)
app.config['SECRET_KEY'] = SECRET_KEY

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    description = db.Column(db.String(150))
    start = db.Column(db.String(150))
    date = db.Column(db.String(150))
    day = db.Column(db.String(150))
    month = db.Column(db.String(150))
    year = db.Column(db.String(150))

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    start = StringField("Start Time", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/home")
def home():
    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day
    
    curr_date = f"{curr_month} {curr_day} {curr_year}"
    home_todo_list = Todo.query.filter_by(date=curr_date).all() #where date = to the present
    return render_template("base.html", home_todo_list=home_todo_list)


@app.route("/calendar", methods=["GET", "POST"])
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
            if str(todos.complete) == 'False':
                date_of_todo.append(todos.date)
                date_of_todo = date_of_todo
            elif str(todos.complete) == 'True':
                comp_date = todos.date + "s" #to diffrentioat between the cmpleted and not
                print(comp_date)
                date_of_todo.append(comp_date)
                date_of_todo = date_of_todo
    return render_template("calendar.html", date_of_todo=date_of_todo)      

@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>', methods=['POST', 'GET'])
def calendarDay(day_hover, monthuser, yearuser):
    curr_month = datetime.date.today().strftime("%B")
    monthuser = curr_month
    day_hover = json.loads(day_hover)
    day_hover = day_hover
    yearuser = json.loads(yearuser)
    date_user = f"{monthuser} {day_hover} {yearuser}"       
    calendar_todo_list = Todo.query.filter(Todo.date.endswith(date_user)).all()

    return render_template('calendarDay.html', monthuser=monthuser , calendar_todo_list=calendar_todo_list, day_hover=day_hover, yearuser=yearuser)

@app.route("/add", methods=["POST"] )
def add():  
    name = request.form.get("name")
    description = request.form.get("description")
    start = request.form.get("start")
    date = request.form.get("day")
    
    punctuation='!?,.:;"\')(_-'
    new_day ='' # Creating empty string
    for i in date:
        if(i not in punctuation):
                    new_day += i
    new_day = new_day.split()

    month = new_day[0]
    day = new_day[1]
    year = new_day[-1]
    date = f'{month} {day} {year}'

    new_todo = Todo(name=name, complete=False, description=description, start=start, date=date, month=month, day=day, year=year)

    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day

    curr_date = f"{curr_month} {curr_day} {curr_year}"

    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>/update/<int:todo_id>', methods=['POST', 'GET'])
def update_cal(todo_id, day_hover, monthuser, yearuser):
    curr_month = datetime.date.today().strftime("%B")
    day_hover = json.loads(day_hover)
    monthuser = curr_month
    yearuser = json.loads(yearuser)

    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("calendarDay", yearuser=yearuser, monthuser=monthuser, day_hover=day_hover, todo_id=todo_id))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/calendar/<day_hover>/<monthuser>/<yearuser>/delete/<int:todo_id>', methods=['POST', 'GET'])
def delete_cal(todo_id, day_hover, monthuser, yearuser):
    curr_month = datetime.date.today().strftime("%B")
    day_hover = json.loads(day_hover)
    monthuser = curr_month
    yearuser = json.loads(yearuser)

    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("calendarDay", yearuser=yearuser, monthuser=monthuser, day_hover=day_hover, todo_id=todo_id))

@app.route("/clear")
def clear():
    curr_month = datetime.date.today().strftime("%B")
    curr_year = datetime.date.today().strftime("%Y")
    now = datetime.datetime.now()
    curr_day = now.day

    curr_date = f"{curr_month} {curr_day} {curr_year}"
    home_todo_list = Todo.query.filter_by(date=curr_date).all()  
    for o in home_todo_list:
        db.session.delete(o)
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

@app.route("/calendar/<day_hover>/<monthuser>/<yearuser>/edit/<int:todo_id>", methods=["GET", "POST"])
def edit_cal(todo_id, day_hover, monthuser, yearuser):
    curr_month = datetime.date.today().strftime("%B")
    day_hover = json.loads(day_hover)
    monthuser = curr_month
    yearuser = json.loads(yearuser)
    form = UserForm()
    name_to_update = Todo.query.get_or_404(todo_id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.description = request.form['description']
        name_to_update.start = request.form['start']
        try:
            db.session.commit()
            return render_template("editCal.html", 
            form=form, 
            name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)
        except:
            return render_template("editCal.html", 
            form=form, 
            name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)
    else:
        return render_template("editCal.html", 
            form=form, 
            name_to_update=name_to_update, day_hover=day_hover , monthuser=monthuser, yearuser=yearuser, todo_id=todo_id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 2000)))