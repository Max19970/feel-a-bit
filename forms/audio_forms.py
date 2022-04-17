from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired


class PublishForm(FlaskForm):
    author = StringField("Автор композиции", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired()])
    genre = StringField("Жанр", validators=[DataRequired()])
    file = FileField("Файл композиции",
                     validators=[FileRequired(), FileAllowed(['mp3'],
                                                             'Для загрузки допускаются только аудиофайлы формата MP3')])
    submit = SubmitField('Опубликовать')
