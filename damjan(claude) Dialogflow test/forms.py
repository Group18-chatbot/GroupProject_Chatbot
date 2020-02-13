from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
#from "folder_with_webapp_in".models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
