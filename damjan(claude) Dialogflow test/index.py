from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session
import os
import dialogflow
import requests
import json
import pusher
from queries import TextBox

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


@app.route('/', methods=['GET', 'POST'])
def send_query():
    form = TextBox()
    try:
        if len(form.query.data)>0:
            userInput = form.query.data
            project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
            fulfillment_text = detect_intent_texts(project_id, "unique", userInput, 'en')
            userInput = "Student:  " + userInput
            response_text = "Claude:  " + fulfillment_text
            return render_template('index.html', response_text=response_text, userInput=userInput, form=form)
    except:
        return render_template('index.html', form=form)
