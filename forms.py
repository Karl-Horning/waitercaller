from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    loginemail = StringField('Email', validators=[DataRequired(), Email()])
    loginpassword = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CreateTableForm(FlaskForm):
    tablenumber = StringField('TableNumber', validators=[DataRequired()])
    submit = SubmitField('Submit')