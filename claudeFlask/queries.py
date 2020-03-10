from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField
from claudeFlask.models import Users

class TextBox(FlaskForm):
    query = StringField('Query')
    submit = SubmitField('Send')
