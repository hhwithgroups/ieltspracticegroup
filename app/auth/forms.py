# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField, \
                    TextAreaField, PasswordField, BooleanField, \
                    FloatField
from wtforms.validators import Email, Required, Length, Regexp, \
                               EqualTo, ValidationError
from wtforms.fields.html5 import DateField
from datetime import date
from ..models import User, level
from .. import app


class RegisterForm(Form):
    email = StringField('Email *',
                validators=[Required(), Length(1, 64), Email()])
    nickname = StringField('Nickname *',
                    validators=[Required(), Length(1, 64)])
    password = PasswordField('Password *',
                    validators=[Required(), Length(1, 64),
                    EqualTo('password2',message='Inconsistent password')])
    password2 = PasswordField('Confirm Password *',
                    validators=[Required(), Length(1, 64)])
    qq = StringField('QQ *',
                     validators=[Required(), Length(1, 64)])
    qq_group = SelectField('QQ Group', coerce=int)
    level = SelectField('Current Level *', default=1,
                        coerce=int, validators=[Required()])
    target_score = FloatField('Target Score')
    exam_passed = BooleanField('I have passed my IELTS exam.')
    date_of_exam = DateField('Date of Exam', default=date.today())
    description = TextAreaField('About Me')
    
    (mon_morning, mon_afternoon, mon_night,
     tue_morning, tue_afternoon, tue_night,
     wed_morning, wed_afternoon, wed_night, 
     thu_morning, thu_afternoon, thu_night,
     fri_morning, fri_afternoon, fri_night,
     sat_morning, sat_afternoon, sat_night,
     sun_morning, sun_afternoon, sun_night) = [BooleanField('')
                                               for i in range(21)]
     
    submit = SubmitField('Submit')
    
    def __init__(self, *args, **kargs):
        super(RegisterForm, self).__init__(*args, **kargs)
        choices = level.items()
        choices.sort()
        self.level.choices = choices
        self.time_segments = (
                self.mon_morning, self.mon_afternoon, self.mon_night,
                self.tue_morning, self.tue_afternoon, self.tue_night,
                self.wed_morning, self.wed_afternoon, self.wed_night, 
                self.thu_morning, self.thu_afternoon, self.thu_night,
                self.fri_morning, self.fri_afternoon, self.fri_night,
                self.sat_morning, self.sat_afternoon, self.sat_night,
                self.sun_morning, self.sun_afternoon, self.sun_night)
        self.qq_group.choices = enumerate(app.config['SPEAKING_QQ_GROUPS'])
        
    # custom validator for email field    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
        
    # custom validator for username field
    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Username already in use.')
        
    def validate_target_score(self, field):
        if field.data > 9 or field.data < 1:
            raise ValidationError('Target score must be 1~9')
        
    def validate_qq(self, field):
        if not field.data.isdigit():
            raise ValidationError('QQ must be all numbers')
        if User.query.filter_by(qq=field.data).first():
            raise ValidationError('QQ number already in use.')
    
    @property
    def available_times(self):
        ret = 0
        for i, t in enumerate(self.time_segments):
            if t.data:
                ret |= (1 << i)
        return ret
        
        
class LoginForm(Form):
    email = StringField('Email', validators=[Required(),
                                            Length(1, 64),
                                            Email()])
    password = PasswordField('Password', validators=[Required(),
                                                     Length(1, 64)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')
    

class ResetPasswordRequestForm(Form):
    email = StringField('Email',
                        validators=[Required(),
                                    Length(1, 64),
                                    Email()])
    submit = SubmitField('OK')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
    
    
class ResetPasswordForm(Form):
    email = StringField('Email',
                        validators=[Required(),
                                    Length(1, 64),
                                    Email()])
    new_password = PasswordField('New password',
                                 validators=[Required(),
                                             EqualTo('password2',
                                                     message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('OK')

        