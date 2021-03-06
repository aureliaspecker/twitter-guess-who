from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired


class InputUsersForm(FlaskForm):
    username = StringField(
        "Input up to 6 Twitter usernames", validators=[DataRequired()]
    )


class SelectForm(FlaskForm):
    select = SelectField("", choices=[], validators=[DataRequired()])


class SelectFormList(FlaskForm):
    select_forms = FieldList(FormField(SelectForm))


class TweetForm(FlaskForm):
    pass
