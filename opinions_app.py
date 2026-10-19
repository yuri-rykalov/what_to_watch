from datetime import datetime
from random import randrange

from flask import Flask, abort, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional


app = Flask(__name__)

# Подключить БД SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = '#HVVJSE#'
# Создать экземпляр SQLAlchemy и в качестве параметра
# передать в него экземпляр приложения Flask.
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Опишем модель данных.
class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    added_by = db.Column(db.String(64))
    


# Класс формы должен быть описан сразу после модели Opinion.
class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[DataRequired(message='Обязательное поле'), Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите мнение о фильме',
        validators=[DataRequired(message='Обязательное поле')]
    )
    source = URLField(
        'Добавьте ссылку на подробный обзор фильма',
        validators=[Length(1, 256), Optional()]
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    # Определить кол-во мнений в БД
    opinion_count = Opinion.query.count()
    # Если мнений нет.
    if not opinion_count:
        abort(500)
    # Иначе выбрать случайное число в диапазоне от 0 до quantity.
    offset_value = randrange(opinion_count)
    opinion = Opinion.query.offset(offset_value).first()
    return render_template('opinion.html', opinion=opinion)


# Тут указывается конвертер пути для id.
@app.route('/opinions/<int:id>')
# Параметром указывается имя переменной.
def opinion_view(id):
    """
    Запрашивает мнение о фильме из БД по ID фильма
    Передает его в шаблон, шаблон тот же, что и для главной страницы.
    """
    opinion = Opinion.query.get_or_404(id)
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    # Создаем новый экземпляр формы.
    form = OpinionForm()
    # Если ошибок не возникло.
    if form.validate_on_submit():
        # Создаем новый экземпляр класса Opinion
        opinion = Opinion(
            # Передаем в него данные, полученные из формы.
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        # Добавляем объект в сессию работы с БД
        db.session.add(opinion)
        # Коммитим изменения
        db.session.commit()
        # Переадресовываем пользователя на страницу с добавленным мнением
        return redirect(url_for('opinion_view', id=opinion.id))
    # Передать объект формы в шаблон add_opinion.html.

    # Если валидация не пройдена - просто отривовать страницу с формой.
    return render_template('add_opinion.html', form=form)

# Тут декорируется обработчик и указывается код нужной ошибки.
@app.errorhandler(500)
def internal_error(error):
    # Ошибка 500 возникает в нештатных ситуациях на сервере. 
    # Например, провалилась валидация данных.
    # В таких случаях можно откатить изменения, незафиксированные в БД,
    # чтобы в базу не записалось ничего лишнего.
    db.session.rollback()
    # Пользователю вернётся страница, сгенерированная на основе шаблона 500
    # Этого шаблона пока нет, но сейчас вы его тоже создадите.
    # Пользователь получит и код HTTP-ответа 500.
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(error):
    # При ошибке 404 в качестве ответа вернётся страница, созданная
    # на основе шаблона 404.html и код HTTP-ответа 404.
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
