# main.py

from flask import render_template, redirect, Blueprint, request, url_for

from app.extensions import db
from app.models import GeneratorConfig

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', titolo="T")


@main.route('/config', methods=['GET', 'POST'])
def config():
    parameters, objlist = GeneratorConfig.parse_config()
    if request.method == 'POST':
        # gc = GeneratorConfig.query.filter_by(id=12).first()
        GeneratorConfig.query.filter_by(id=12).update(
            {'conf_tip': 'pare funzioni'}
        )
        # gc.conf_tip = 'Nome file indice'
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('config.html',
                           parameters=parameters, title='Configurazione')


@main.route('/generator', methods=['GET', 'POST'])
def generator():
    return "<h3>Test</h3>"


@main.route('/new_article', methods=['GET', 'POST'])
def new_article():
    return "<h3>Test</h3>"
