from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired

class InputUsersForm(FlaskForm):
    username = StringField('Input Up To 6 Twitter Usernames', validators=[DataRequired()])

class SelectForm(FlaskForm):
    select = SelectField('', choices=[], validators=[DataRequired()])

class SelectFormList(FlaskForm):
    select_forms = FieldList(FormField(SelectForm))



