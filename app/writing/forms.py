__author__ = 'wei'

from flask.ext.wtf import Form
from wtforms import SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import Required, Length
from ..models import WritingCategory

class ArticleForm(Form):
    # category = SelectField('Category', coerce=int)
    # topic = TextAreaField('Topic *', validators=[Required(), Length(1, 1024)])
    # issue = SelectField('Issue', coerce=int)
    content = TextAreaField('Content',
                            validators=[Required(),
                                        Length(min=200)])
    submit = SubmitField('Submit')

    # def __init__(self, *args, **kargs):
    #     super(ArticleForm, self).__init__(*args, **kargs)
    #     choices = WritingCategory.query \
    #                              .with_entities(WritingCategory.id,
    #                                             WritingCategory.category).all()
    #     choices.sort()
    #     self.category.choices = choices


class CommentForm(Form):
    content = TextAreaField('Content', validators=[Required()])
    submit = SubmitField('Comment')


class AnnotationForm(Form):
    content = TextAreaField('Content', validators=[Required()])
    start = HiddenField('')
    end = HiddenField('')
    submit = SubmitField('Annotate')