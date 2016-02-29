from flask.ext.wtf import Form
from wtforms import SubmitField, SelectField, StringField, TextAreaField
from wtforms.validators import Required, Length
from ..models import WritingCategory

class CategoryForm(Form):
    category = StringField('New Category', validators=[Required(), Length(1, 64)])
    submit = SubmitField('Submit')

class TopicForm(Form):
    topic = TextAreaField('New Topic', validators=[Required()])
    submit = SubmitField('Submit')