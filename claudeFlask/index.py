from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_login import login_user, current_user, logout_user, login_required
import os
import re
import dialogflow
import requests
import json
import pusher
from claudeFlask import app, db
from claudeFlask.models import *
from claudeFlask.queries import TextBox
from claudeFlask.forms import *
from datetime import date, timedelta, datetime
import mysql.connector
from claudeFlask.models import db, Calendar


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


def gradeQuery(response_text,userInput):
    print(userInput)

    #make users input a list
    user_Input_split = (userInput.upper()).split()

    if "grades" in response_text:
        #display grades from database for now going to use a local text file
        user_id = current_user.id

        #contains grades of the current user
        grades=Grades.query.filter_by(id=user_id)

        print(user_Input_split)


        #table based querying
        ModuleCodequery = []
        ModuleNamequery = []
        moduleGradePercentageQuery = []

        for grade in grades:

            if grade.ModuleCode.upper() in user_Input_split:
                ModuleCodequery.append(grade.ModuleCode)

            #some modulenames have spaces so need a different approach
            ModuleNamesplit = (grade.ModuleName.upper()).split()
            if all(elem in user_Input_split for elem in ModuleNamesplit ):
                    ModuleNamequery.append(grade.ModuleName)

            if str(grade.GradePercentage) in user_Input_split:
                    moduleGradePercentageQuery.append(grade.GradePercentage)


        grades = grades.filter(( Grades.ModuleCode.in_(ModuleCodequery))  | (Grades.ModuleName.in_(ModuleNamequery) | (Grades.GradePercentage.in_(moduleGradePercentageQuery)) ))

        #if no table querying requested
        if (len(ModuleCodequery) == 0) & (len(ModuleNamequery) == 0) & (len(moduleGradePercentageQuery ) == 0):
            grades=Grades.query.filter_by(id=user_id)

        return grades
    else:
            return


def sportQuery(response_text, user_Input):
    response_text_split = response_text.split()
    user_Input_split = (user_Input.upper()).split()
    if "sports" in response_text_split:
        sports=Sports.query.all()

        Sportsquery = []
        Teamquery1 = []
        Teamquery2 = []

        for sport in sports:


            if (sport.Sport).upper() in user_Input_split:
                Sportsquery.append(sport.Sport)

            #some modulenames have spaces so need a different approach
            team1 = sport.Team1
            team2 = sport.Team2
            teamName1split = (team1.upper()).split()
            teamName2split = (team2.upper()).split()

            if all(elem in user_Input_split for elem in teamName1split ) & (team1 not in Teamquery1):
                Teamquery1.append(sport.Team1)

            if all(elem in user_Input_split for elem in teamName2split ) & (team2 not in Teamquery2):
                Teamquery2.append(sport.Team2)


        sports = Sports.query.filter(( Sports.Sport.in_(Sportsquery))  | (Sports.Team1.in_(Teamquery1) | (Sports.Team2.in_(Teamquery2)) ))

        #if no table querying requested
        if (len(Sportsquery) == 0) & (len(Teamquery1) == 0) & (len(Teamquery2 ) == 0):
            sports=Sports.query.all()


        return sports
    else:
            return

def getWeekDate(today):
    startDay = today - timedelta(days=today.weekday())
    addDay = startDay.strftime("%Y-%m-%d")
    week = []
    for i in range(7):
        week.append(addDay)
        startDay = startDay + timedelta(days=1)
        addDay = startDay.strftime("%Y-%m-%d")
    return(week)

def getMonthDate(today):
    print(today)
    startDay = today - timedelta(days=int(today.strftime("%d"))-1)
    addDay = startDay.strftime("%Y-%m-%d")
    month = []
    mDay = startDay
    mSize = 0
    mCheck = True
    while mCheck:
        if mDay.strftime("%m") == today.strftime("%m"):
            mSize = mSize + 1
            mDay = mDay + timedelta(days=1)
        else:
            mCheck = False
    for i in range(mSize):
        month.append(addDay)
        startDay = startDay + timedelta(days=1)
        addDay = startDay.strftime("%Y-%m-%d")
    return(month)


def timetableQuery(response_text, user_Input):
    #Damjan prototype
    #testing query for timetable
    response_text_split = response_text.split()
    user_Input_split = user_Input.split()
    
    if "week" in response_text_split and "timetable" in response_text_split and "previous" in response_text_split:
        user_id = current_user.id
        today = date.today()
        week = getWeekDate(today - timedelta(days=7))
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(week))
        return timetable

    if "week" in response_text_split and "timetable" in response_text_split and "next" in response_text_split:
        #print("test1")
        user_id = current_user.id
        today = date.today()
        #print("test2")
        week = getWeekDate(today + timedelta(days=7))
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(week))
        return timetable

    if "week" in response_text_split and "timetable" in response_text_split:
        user_id = current_user.id
        today = date.today()
        week = getWeekDate(today)
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(week))
        return timetable

    if "month" in response_text_split and "timetable" in response_text_split and "previous" in response_text_split:
        user_id = current_user.id
        today = date.today()
        month = getMonthDate(today - timedelta(days=int(today.strftime("%d"))))
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(month))
        return timetable

    if "month" in response_text_split and "timetable" in response_text_split and "next" in response_text_split:
        #print("test1")
        user_id = current_user.id
        today = date.today()
        #print("test2")
        mDay = today - timedelta(days=int(today.strftime("%d"))-1)
        mSize = 0
        mCheck = True
        while mCheck:
            if mDay.strftime("%m") == today.strftime("%m"):
                mSize = mSize + 1
                mDay = mDay + timedelta(days=1)
            else:
                mCheck = False
        #print(mSize)
        #print(int(today.strftime("%d")))
        month = getMonthDate(today + (timedelta(days=mSize)))
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(month))
        return timetable

    if "month" in response_text_split and "timetable" in response_text_split:
        user_id = current_user.id
        today = date.today()
        month = getMonthDate(today)
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(month))
        return timetable

    if "timetable" in response_text_split:
        user_id = current_user.id
        dates = Timetable.query.filter_by(id=user_id)
        Ddate = user_Input_split[-3] + "-" + user_Input_split[-2] + "-" + user_Input_split[-1]
        daysQuery = []
        for day in dates:
            if day.Date == Ddate:
                daysQuery.append(day.Date)
        timetable = Timetable.query.filter_by(id=user_id).filter(Timetable.Date.in_(daysQuery))
        return timetable

    else:
        return


def calendarQuery(response_text):
    response_text_split = response_text.split()
    if "event" in response_text_split:
        user_id = current_user.id
        event = Calendar(id=user_id,Date="sdf",Time="sdf",Reminder="sdf",Type="sdf")
        db.session.add(event)
        db.session.commit()
        return
    else:
        return

#def calendar_addQuery(response_text):
#    response_text_split = response_text.split()
#
 #   mydb = mysql.connector.connect(
 #   host="csmysql.cs.cf.ac.uk",
 #   user="CM2305.group18.1920",
 #   passwd="Mw2Z4DeYMm62fPG",
  #  database="CM2305_group18_1920"
  #  )
  #  mycursor = mydb.cursor()
 #   if "event" in response_text_split:
  #      sql = "INSERT INTO calendar (id, Date, Time, Reminder, Type) VALUES (%s, %s,%s, %s)"
  #      val = (7,"John", "Highway 21","John", "Highway 21")
  #      mycursor.execute(sql, val)
  #      mydb.commit()
   #     return
   # else:
   #     return
    





def calendar_deleteQuery(response_text):
    response_text_split = response_text.split()
    if "delete" in response_text_split:
        user_id = current_user.id
        event = Calendar(date='sdf',time='sdf',reminder='sdf',type='sdf')
        db.session.add(event)
        db.session.commit()
        return event
    else:
        return


@app.route('/query', methods=['GET', 'POST'])
def send_query():
        if current_user.is_authenticated:
            form = TextBox()
            try:
                if len(form.query.data)>0:

                    userInput = form.query.data
                    #remove special characters
                    userInput = re.sub(r'[^a-zA-Z0-9]', ' ', userInput)

                    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
                    fulfillment_text = detect_intent_texts(project_id, "unique", userInput, 'en')
                    userInput = "Student:  " + userInput
                    response_text = "Cymro:  " + fulfillment_text
                    grades = gradeQuery(response_text, userInput)
                    timetable = timetableQuery(response_text, userInput)
                    sports = sportQuery(response_text, userInput)
                    calendar = calendarQuery(response_text)




                    return render_template('index.html', response_text=response_text, userInput=userInput, form=form, grades=grades, timetable = timetable, sports=sports)
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
