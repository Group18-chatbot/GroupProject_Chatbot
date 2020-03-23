from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
import os
import dialogflow
import requests
import json
import pusher
from claudeFlask import app,db
from claudeFlask.models import *
from claudeFlask.queries import TextBox
from claudeFlask.forms import *

if __name__ == "__main__":
	app.run()
 
def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text


def gradeQuery(response_text):
    response_text_split = response_text.split()
    print(response_text_split)
    if "grades" in response_text:
        #display grades from database for now going to use a local text file
        user_id = current_user.id
        #contains grades of the current user
        grades=Grades.query.filter_by(id=user_id)
        # to display
        # for grade in grades:
        # print(grade)

        for grade in grades:
                print(grade)
        return grades
    else:
            return


def sportQuery(response_text):
    response_text_split = response_text.split()
    print(response_text_split)
    if "sports" in response_text_split:
        sports=Sports.query.all()


        for sport in sports:
                print(sport)
        return sports
    else:
            return


def timetableQuery(response_text):
    #Damjan prototype
    #testing query for timetable
    response_text_split = response_text.split()
    timetableDict= {}
    if "month" in response_text_split and "timetable" in response_text_split:
        print('example table for month...')
        f = open("timetable.txt", "r")
        for x in f:
            key = x.split()[0]
            timetableDict[key] = x.split()[1]
        return timetableDict
    elif "week" in response_text_split and "timetable" in response_text_split:
        print('example table for week...')
        f = open("timetable.txt", "r")
        for x in f:
            key = x.split()[0]
            timetableDict[key] = x.split()[1]
        return timetableDict
    else:
            return


#@app.route("/")
@app.route('/query', methods=['GET', 'POST'])
def send_query():
        if current_user.is_authenticated:
            form = TextBox()
            try:
                if len(form.query.data)>0:
                    userInput = form.query.data
                    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
                    fulfillment_text = detect_intent_texts(project_id, "unique", userInput, 'en')
                    userInput = "Student:  " + userInput
                    response_text = "Claude:  " + fulfillment_text
                    grades = gradeQuery(response_text)
                    timetableDict = timetableQuery(response_text)
                    sports = sportQuery(response_text)

                    return render_template('index.html', response_text=response_text, userInput=userInput, form=form, grades=grades, timetableDict = timetableDict, sports=sports)
            except:
                return render_template('index.html', form=form)
        else:
            flash("Please login to acces the chatbot")
            return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    logout_user()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data,email=form.email.data,password=form.password.data)


        db.session.add(user)
        db.session.commit()
        # Create a row in the cart database and wishlist database for 1 user

        return redirect("login")
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated == False:
        print(current_user)
        form = LoginForm()
        if form.validate_on_submit():
                user = Users.query.filter_by(email=form.email.data).first()
                if user is not None and user.verify_password(form.password.data):
                        login_user(user)
                        flash("You are now logged in")
                        return redirect("query") #check what url should be here
                flash("Invalid username or password")
        return render_template('login.html', form=form)
    else:
        form = TextBox()
        return redirect("query")

@app.route("/logout")
def logout():
        logout_user()
        session.clear() #do we have sessions that need to be cleared???
        flash("You have been logged out")
        return redirect(url_for("login")) ##where home should be pre login

@app.route('/')
@app.route('/home')
def home():
        #return render_template(url_for("home"), title="Home")
        return render_template('home.html', title='Home')
