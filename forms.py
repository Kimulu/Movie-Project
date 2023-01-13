from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

class RateMovieForm(FlaskForm):
    rating = StringField(label='rating',validators=[DataRequired()])
    review = StringField(label='review',validators=[DataRequired()])
    submit = SubmitField(label="submit")

class NewMovieForm(FlaskForm):
    title = StringField(label='rating',validators=[DataRequired()])
    submit = SubmitField(label="submit")

class CreateListForm(FlaskForm):
    list_name =StringField(label='List Name',validators=[DataRequired()])
    submit= SubmitField(label="submit")