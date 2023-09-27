from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class EditUserForm(FlaskForm):
    """Form for editing users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=3, max=20)])
    image_url = StringField('(Optional) Profile Image URL')
    header_image_url = StringField('Header Image URL')
    bio = TextAreaField('Bio', validators=[Length(max=150)])
    location = StringField('Location')
    password = PasswordField('Password', validators=[DataRequired()])
    # new_password = PasswordField('New Password', validators=[DataRequired()])
    # confirm_new_password = PasswordField(
    #     'Confirm New Password', validators=[DataRequired()])


class AddLikesForm(FlaskForm):
    """Form for adding likes."""
    id = HiddenField('id', validators=[DataRequired()])
    update = HiddenField('update', validators=[DataRequired()])
