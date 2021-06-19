from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (StringField,
                     TextAreaField,
                     SubmitField,
                     PasswordField,
                     DateField,
                     SelectField,
					 TextField)
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                URL,
								Optional)



								

class SignupForm(FlaskForm):
    """User Sign-up Form."""
    username = StringField(
        'Lietotājvārds',
        validators=[DataRequired()]
    )
    email = StringField(
        'E-pasta adrese',
        validators=[
            Length(min=6),
            Email(message='Ievadiet derīgu e-pasta adresi'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Parole',
        validators=[
            DataRequired(),
            Length(min=6, message='Izvēlēties spēcīgāku paroli')
        ]
    )
    confirm = PasswordField(
        'Apstiprināt paroli',
        validators=[
            DataRequired(),
            EqualTo('password', message='Parolēm ir jāsakrīt')
        ]
    )
    name = StringField(
        'Uzņēmuma nosaukums',
        validators=[Optional()]
    )
    submit = SubmitField('Reģistrēt')
	
class LoginForm(FlaskForm):
	"""User Log-in Form."""
	#email = StringField(
	#    'Email',
	#    validators=[
	#        DataRequired(),
	#        Email(message='Enter a valid email.')
	#    ]
	#)
	username = StringField(
		'Lietotājvārds',
		validators=[DataRequired()]
	)
	password = PasswordField('Parole', validators=[DataRequired()])
	submit = SubmitField('Ienākt')


class ContactForm(FlaskForm):
    """Contact form."""
    name = StringField('Name', [
        DataRequired()])
    email = StringField('Email', [
        Email(message=('Not a valid email address.')),
        DataRequired()])
    body = TextField('Message', [
        DataRequired(),
        Length(min=4, message=('Your message is too short.'))])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')