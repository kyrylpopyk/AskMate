from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask import session
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# from askmate.data_manager import choice_query


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    picture = FileField('Upload picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Sign Up')

    # def validate_email(self, email):
        # find email in dadabase
        # if user:
        #     raise ValidationError('That email is taken. Choose a different one.')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=20)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    picture = FileField('Change picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')

    # def validate_email(self, email):
    #     if email.data != session.email:
    #         # find username by email
    #         if user:
    #             raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class QuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=10, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=20)])
    image = FileField('Upload image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    # tag_name = QuerySelectField('Tag', allow_blank=True, validators=[DataRequired()], query_factory=choice_query, get_label='tag_name')
    submit = SubmitField('Post')


# class TagForm(FlaskForm):
#     tag_id = IntegerField('tag_id')
#     tag_name = SelectField('Tag', validators=[DataRequired()], choices=['choose...', *get_all_tag_names()])
#
# class QuestionTagForm(FlaskForm):
#     question_id = IntegerField('question_id')
#     tag_id = IntegerField('tag_id')
