from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateTimeField, DateField, TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class RegistrationForm(FlaskForm):
    # user_id = IntegerField('user_id',
    #                             validators=[DataRequired(),])

    username = StringField('user_name',
                           validators=[DataRequired(message="Enter username"), Length(min=3, max=20)])

    selected_date = DateField('selected_date',
                               format='%Y-%m-%d',
                               validators=[DataRequired()])

    start_time = TimeField('start_time',
                           format='%H:%M',
                           validators=[DataRequired()])

    end_time = TimeField('end_time',
                         format='%H:%M',
                         validators=[DataRequired()])

    people_count = IntegerField('people_count',
                                validators=[DataRequired(), NumberRange(min=2, max=21, message="Enter people count!")])

    selected_style = StringField('selected_style',
                                 validators=[DataRequired(), Length(max=100)])  # Ограничение на 100 символов

    preferences = StringField('preferences',
                              validators=[Length(max=200)])  # Ограничение на 200 символов

    city = StringField('city',
                       validators=[Length(max=100)])  # Ограничение на 100 символов

    submit = SubmitField('Sign Up')
