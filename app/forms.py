# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, StringField, TextAreaField, SubmitField,
    SelectField, DateField
)

from wtforms.validators import DataRequired, InputRequired, NumberRange\
    , ValidationError
# from flask_ckeditor import CKEditorField


def validate_category(form, field):
    """Verifica se la selezione da un combo è stata effettuata"""
    if field.data < 0:  # il codice selezione per il placeholder deve essere <0
        raise ValidationError('Selezione non valida')


class ArticleBoilerplate(FlaskForm):
    """Il testo boilerplate iniziale"""
    text = TextAreaField()


class BuilderLog(FlaskForm):
    """Report operazione di creazione file html"""
    log = TextAreaField()


class NewArticleForm(FlaskForm):
    """Creazione voce db per un nuova articolo"""
    template = StringField('templatename')
    name = StringField('articlename',
                       validators=[DataRequired(
                           message='Campo Obbligatorio'
                       )])
    description = TextAreaField('articledescr', validators=[DataRequired()])
    purpose = TextAreaField('articlenpurpos', validators=[DataRequired()])
    categ = SelectField('categ', coerce=int, validators=[
        validate_category])
    publish_date = DateField('publishdate', format='%Y-%m-%d',
                             validators=[DataRequired()])
    add_to_index = BooleanField('addtoindex', default=True)
    # editor = CKEditorField('test')


class CategoryForm(FlaskForm):
    """Categoria"""
    descr = StringField('catname')


class HTMLGeneratorForm(FlaskForm):
    """Generatore articolo html"""
    modules = StringField('modules' )
    rebuild_index = BooleanField('rebindex', default=False)
    rebuild_table = BooleanField('rebtbl', default=False)
    spellcheck = BooleanField('spcheck', default=False)
    fixed_sidebar = BooleanField('sbfixed', default=True)
    privacy_page = BooleanField('privacyPage', default=False)


class ConfigurationForm(FlaskForm):
    """Configurazione procedura"""
    submit = SubmitField('Modifica configurazione')


class SourceForm(FlaskForm):
    """Sorgente articolo"""
    source_text = TextAreaField()


class SearchArticlesForm(FlaskForm):
    filter_text = StringField('filterText', validators=[DataRequired()])
