from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField,\
    BooleanField, StringField, IntegerField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    avatar_img = FileField('Файл аватара',
                           validators=[FileAllowed(['png', 'jpg', 'jpeg'],
                                                   'Для загрузки картинки аватара доступны '
                                                   'только форматы PNG и JPG/JPEG')])
    repeat_password = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    role = SelectField('Роль', choices=[(1, 'Слушатель'), (2, 'Музыкант')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
