from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, FloatField, IntegerField, SelectField, DateField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
from app.models import User, StudentProfile


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class StudentRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    roll_number = StringField('Roll Number / Student ID', validators=[DataRequired(), Length(min=2, max=50)])
    branch = SelectField('Engineering Branch / Discipline', choices=[
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Data Science & AI', 'Data Science & AI')
    ], validators=[DataRequired()])
    cgpa = FloatField('CGPA (0.0 - 10.0)', validators=[DataRequired(), NumberRange(min=0.0, max=10.0)])
    graduation_year = IntegerField('Graduation Year', validators=[DataRequired(), NumberRange(min=2020, max=2035)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    skills = StringField('Key Skills (comma separated)', validators=[Optional(), Length(max=255)])
    resume = FileField('Resume (PDF only)', validators=[Optional(), FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register as Student')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('This email is already registered. Please log in or use another email.')

    def validate_roll_number(self, field):
        if StudentProfile.query.filter_by(roll_number=field.data.strip().upper()).first():
            raise ValidationError('This roll number is already registered.')


class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Official Corporate Email', validators=[DataRequired(), Email()])
    website = StringField('Website URL', validators=[Optional(), Length(max=255)])
    industry = SelectField('Industry Domain', choices=[
        ('Information Technology & Software', 'Information Technology & Software'),
        ('Consulting & Financial Services', 'Consulting & Financial Services'),
        ('Core Engineering & Manufacturing', 'Core Engineering & Manufacturing'),
        ('E-commerce & Retail', 'E-commerce & Retail'),
        ('Telecommunications', 'Telecommunications'),
        ('Healthcare & Biotech', 'Healthcare & Biotech'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    contact_person = StringField('Primary Contact Person', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    description = TextAreaField('Company Overview', validators=[Optional(), Length(max=1000)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register Company')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('This email is already registered.')


class StudentProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    branch = SelectField('Branch', choices=[
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Data Science & AI', 'Data Science & AI')
    ], validators=[DataRequired()])
    cgpa = FloatField('CGPA', validators=[DataRequired(), NumberRange(min=0.0, max=10.0)])
    graduation_year = IntegerField('Graduation Year', validators=[DataRequired(), NumberRange(min=2020, max=2035)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    skills = StringField('Key Skills (comma separated)', validators=[Optional(), Length(max=255)])
    resume = FileField('Update Resume (PDF only)', validators=[Optional(), FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    submit = SubmitField('Save Profile')


class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField('Job Description & Requirements', validators=[DataRequired(), Length(min=10)])
    location = StringField('Job Location (e.g., Bangalore, Hybrid, Remote)', validators=[DataRequired(), Length(max=100)])
    package_lpa = FloatField('Annual CTC / Package (in LPA, e.g. 14.5)', validators=[DataRequired(), NumberRange(min=0.1)])
    required_skills = StringField('Required Skills (e.g., Python, SQL, Docker)', validators=[DataRequired(), Length(max=255)])
    min_cgpa = FloatField('Minimum CGPA Cutoff', validators=[DataRequired(), NumberRange(min=0.0, max=10.0)])
    deadline = DateField('Application Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    is_active = BooleanField('Active & Accepting Applications', default=True)
    submit = SubmitField('Submit Job Posting')


class ApplicationStatusUpdateForm(FlaskForm):
    status = SelectField('Application Status', choices=[
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected / Placed')
    ], validators=[DataRequired()])
    feedback = TextAreaField('Feedback / Remarks for Candidate', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')
