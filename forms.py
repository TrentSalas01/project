from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    """
    Class to create form for registration
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=20)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password"), Length(min=8, max=20)],
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    """
    Class to create form for login
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember = BooleanField('Remember Me')
    submit = SubmitField("Login")


class ItemAddForm(FlaskForm):
    """
    Class to create form for adding an item
    """

    text = StringField("Description", validators=[DataRequired()])
    photo = FileField(
        "Your Photo",
        validators=[FileRequired(), FileAllowed(["jpg", "png", "jpeg"], "Images Only")],
    )
    name = StringField("Item Name", validators=[DataRequired()])
    submit = SubmitField("Add")


class CreateCommunityForm(FlaskForm):
    """
    Class to create form to create a community
    """

    name = StringField("Community Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Create")


class DeleteCommunityForm(FlaskForm):
    """
    Class to create a form to delete a community
    """

    deletename = StringField("Community to Delete", validators=[DataRequired()])
    submit = SubmitField("Delete")


class CreateCollectionForm(FlaskForm):
    """
    Class to create a form to create a collection
    """

    name = StringField("Name of collection", validators=[DataRequired()])
    desc = StringField("Description of collection", validators=[DataRequired()])
    submit = SubmitField("Create Collection")


class CreatePostForm(FlaskForm):
    """
    Class to create a form to create a post
    """

    title = StringField("Title", validators=[DataRequired()])
    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Post!")


class EditPostForm(FlaskForm):
    """
    Class to create a form to edit a post
    """

    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Save")


# class EditItemForm(FlaskForm):


class DeletePostForm(FlaskForm):
    """
    Class to create a form to delete a post
    """

    submitConfirm = SubmitField("Confirm")
    submitCancel = SubmitField("Cancel")


class DeleteItemForm(FlaskForm):
    """
    Class to create a form to delete an item
    """

    submitConfirm = SubmitField("Confirm")
    submitCancel = SubmitField("Cancel")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=3, max=20)])
    """
    Class to create a form to change a user's settings
    """
    email = StringField("Email", validators=[Email()])
    bio = StringField("Biography")
    profile_picture = SelectField(
        "Profile Picture",
        choices=[
            ("lion", "Lion"),
            ("eagle", "Eagle"),
            ("zebra", "Zebra"),
            ("snake", "Snake"),
            ("pony", "Pony"),
        ],
    )
    submit = SubmitField("Submit")


class CreateCommentForm(FlaskForm):
    """
    Class to create a form to create a comment
    """

    text = TextAreaField("Leave a comment below...", validators=[DataRequired()])
    submit = SubmitField("Post!")
