# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField, \
                    TextAreaField, BooleanField, FloatField
from wtforms.validators import Required, Optional, Length, ValidationError
from wtforms.fields.html5 import DateField
from ..models import User, level

    
class ProfileForm(Form):
    qq = StringField('QQ', validators=[Length(0, 11), Optional()])
    wechat_id = StringField('WeChat ID', validators=[Length(0, 20), Optional()])
    level = SelectField('Current Level', coerce=int, default=2, validators=[Required()])
    target_score = FloatField('Target Score', validators=[Optional()])
    exam_passed = BooleanField('I have passed my IELTS exam.')
    date_of_exam = DateField('Date of Exam', validators=[Optional()])
    description = TextAreaField('About Me')
    
    (mon_morning, mon_afternoon, mon_night,
     tue_morning, tue_afternoon, tue_night,
     wed_morning, wed_afternoon, wed_night, 
     thu_morning, thu_afternoon, thu_night,
     fri_morning, fri_afternoon, fri_night,
     sat_morning, sat_afternoon, sat_night,
     sun_morning, sun_afternoon, sun_night) = [BooleanField('') for i in range(21)]
     
    submit = SubmitField('Submit')

     
    def __init__(self, *args, **kargs):
        super(ProfileForm, self).__init__(*args, **kargs)
        choices = level.items()
        choices.sort()
        self.level.choices = choices
        self.time_segments = (self.mon_morning, self.mon_afternoon, self.mon_night,
                              self.tue_morning, self.tue_afternoon, self.tue_night,
                              self.wed_morning, self.wed_afternoon, self.wed_night, 
                              self.thu_morning, self.thu_afternoon, self.thu_night,
                              self.fri_morning, self.fri_afternoon, self.fri_night,
                              self.sat_morning, self.sat_afternoon, self.sat_night,
                              self.sun_morning, self.sun_afternoon, self.sun_night)
        
    @property
    def available_times(self):
        ret = 0
        for i, t in enumerate(self.time_segments):
            if t.data:
                ret |= (1 << i)
        return ret

    @available_times.setter
    def available_times(self, value):
        for i in range(len(self.time_segments)):
            self.time_segments[i].data = ((value >> i) & 1 == 1)

    def validate_qq(self, field):
        if not field.data.isdigit():
            raise ValidationError('QQ must be all numbers')
        # Should not check this way, the QQ number is used by current user
        # if User.query.filter_by(qq=field.data).first():
        #     raise ValidationError('QQ number already in use.')
