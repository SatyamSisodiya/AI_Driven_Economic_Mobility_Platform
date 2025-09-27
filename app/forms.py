from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Optional

class UserProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired()])
    current_role = StringField('Current Role')
    experience_years = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0, max=50)])
    education_level = SelectField('Education Level', 
                                choices=[('high_school', 'High School'),
                                        ('associates', 'Associate\'s Degree'),
                                        ('bachelors', 'Bachelor\'s Degree'),
                                        ('masters', 'Master\'s Degree'),
                                        ('phd', 'Ph.D. or Doctorate')])
    location = StringField('Location')
    target_role = StringField('Target Role', validators=[DataRequired()])
    target_salary = IntegerField('Target Salary ($)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Profile')

class SkillForm(FlaskForm):
    skill_name = StringField('Skill Name', validators=[DataRequired()])
    proficiency_level = SelectField('Proficiency Level',
                                  choices=[(1, 'Beginner'),
                                          (2, 'Elementary'),
                                          (3, 'Intermediate'),
                                          (4, 'Advanced'),
                                          (5, 'Expert')],
                                  coerce=int,
                                  validators=[DataRequired()])
    submit = SubmitField('Add Skill')