from datetime import datetime
from random import randrange

from flask import Flask, render_template, redirect, url_for
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


# Опишем модель данных.
class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


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
        return 'В базе данных мнений о фильмах нет.'
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


if __name__ == '__main__':
    app.run()
