# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, StringField, TextAreaField, SubmitField,
    SelectField
)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired
# from flask_ckeditor import CKEditorField


class BuilderLog(FlaskForm):

    log = TextAreaField()


class NewArticleForm(FlaskForm):

    template = StringField('templatename')
    name = StringField('articlename')
    description = TextAreaField('articledescr')
    purpose = TextAreaField('articlenpurpos')
    categ = SelectField('categ')
    publish_date = DateField('publishdate', format='%Y-%m-%d')
    add_to_index = BooleanField('addtoindex', default=True)
    # editor = CKEditorField('test')


class CategoryForm(FlaskForm):
    descr = StringField('catname')


class HTMLGeneratorForm(FlaskForm):

    modules = StringField('modules', validators=[DataRequired()])
    rebuild_index = BooleanField('rebindex', default=False)
    rebuild_table = BooleanField('rebtbl', default=False)
    spellcheck = BooleanField('spcheck', default=False)
    fixed_sidebar = BooleanField('sbfixed', default=True)


class ConfigurationForm(FlaskForm):
    submit = SubmitField('Modifica configurazione')

