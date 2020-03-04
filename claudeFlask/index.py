from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session
import os
import dialogflow
import requests
import json
import pusher
from queries import TextBox
#from claudeFlask import templates
from templates import *
from forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a6295f93be3b219d7fe9eaccdb60bbb3ff7f29b09ab2507e'

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
	gradesDict= {}
	if "grades" in response_text:
		#display grades from database for now going to use a local text file
		f = open("grades.txt", "r")
		for x in f:
			key = x.split()[0]
			gradesDict[key] = x.split()[1]
		print(gradesDict)	
	return gradesDict

#@app.route("/")
@app.route('/query', methods=['GET', 'POST'])
def send_query():
    form = TextBox()
    try:
        if len(form.query.data)>0:
            userInput = form.query.data
            project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
            fulfillment_text = detect_intent_texts(project_id, "unique", userInput, 'en')
            userInput = "Student:  " + userInput
            response_text = "Claude:  " + fulfillment_text
            gradesDict = gradeQuery(response_text)
            return render_template('index.html', response_text=response_text, userInput=userInput, form=form, gradesDict=gradesDict)
    except:
        return render_template('index.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
        form = LoginForm()
        if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                if user is not None and user.verify_password(form.password.data):
                        login_user(user)
                        flash("You are now logged in")
                        return redirect(url_for("home")) #check what url should be here
                flash("Invalid username or password")
        return render_template('login.html', title="Login", form=form)

@app.route("/logout")
def logout():
        logout_user()
        session.clear() #do we have sessions that need to be cleared???
        flash("You have been logged out")
        return redirect(url_for("home"), title="Home") ##where home should be pre login

@app.route('/')
@app.route('/home')
def home():
        #return render_template(url_for("home"), title="Home")
        return render_template('home.html', title='Home')
