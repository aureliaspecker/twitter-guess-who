from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class InputUsersForm(FlaskForm):
    username = StringField('Input User', validators=[DataRequired()])
