from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired


class PublishForm(FlaskForm):
    author = StringField("Автор композиции", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired()])
    genre = StringField("Жанр", validators=[DataRequired()])
    file = FileField("Файл композиции", validators=[FileRequired()])
    submit = SubmitField('Опубликовать')
