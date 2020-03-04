from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField

class TextBox(FlaskForm):
    query = StringField('Query')
    submit = SubmitField('Send')