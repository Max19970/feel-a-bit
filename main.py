import os

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename

import datetime as dt
from mutagen.mp3 import MP3

from forms.user_forms import RegisterForm, LoginForm
from forms.audio_forms import PublishForm
from data.users import User
from data.audio import Audio
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/audio'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/dataB.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/main")


@app.route('/')
@app.route('/index/')
def index():
    return render_template('title.html', title='Feel A Bit')


@app.route('/main')
def site_main():
    db_session.global_init('db/dataB.db')
    db_sess = db_session.create_session()
    audios = []
    for audio in db_sess.query(Audio).all():
        publisher_name = db_sess.query(User).filter(User.id == audio.publisher).first()
        publisher_name = publisher_name.surname + ' ' + publisher_name.name
        audio_likers = map(int, audio.likers.split()) if audio.likers else []
        audio_dislikers = map(int, audio.dislikers.split()) if audio.dislikers else []
        audios.append([audio.publisher, audio.author, audio.file, audio.name,
                       audio.genre, publisher_name, audio.id, audio.likes,
                       audio.dislikes, audio_likers, audio_dislikers])
    return render_template('main.html', audios=audios)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже зарегистрирован!")
        user = User(
            email=form.email.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        return render_template('login.html',
                               message="Ошибка! Логин или пароль введены неверно",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/publish',  methods=['GET', 'POST'])
@login_required
def publish():
    form = PublishForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        audio = Audio(
            publisher=current_user.id,
            author=form.author.data,
            name=form.name.data,
            genre=form.genre.data,
            file=f'static/audio/{filename}',
            publish_date=dt.datetime.now(),
        )
        audio.duration = MP3(audio.file).info.length
        db_sess.add(audio)
        db_sess.commit()
        return redirect('/main')
    return render_template('audio_x.html', title='Добавление песни',
                           form=form)


@app.route('/audio/<int:audio_id>', methods=['GET', 'POST'])
@login_required
def edit_audio(audio_id):
    form = PublishForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        audio = db_sess.query(Audio).filter(Audio.id == audio_id, Audio.publisher == current_user.id).first()
        if audio:
            form.author.data = audio.author
            form.name.data = audio.name
            form.genre.data = audio.genre
            form.file.data = audio.file
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        audio = db_sess.query(Audio).filter(Audio.id == audio_id, Audio.publisher == current_user.id).first()
        if audio:
            audio.author = form.author.data
            audio.name = form.name.data
            audio.genre = form.genre.data
            audio.file = form.file.data
            db_sess.commit()
            return redirect('/main')
        else:
            abort(404)
    return render_template('audio_x.html',
                           title='Редактирование песни',
                           form=form
                           )


@app.route('/delete/<int:audio_id>', methods=['GET', 'POST'])
@login_required
def audio_delete(audio_id):
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id, Audio.publisher == current_user.id).first()
    if audio:
        db_sess.delete(audio)
        audios = []
        for audio in db_sess.query(Audio).all():
            audios.append(audio)
        for audio in db_sess.query(Audio).all():
            audio.id = audio.index(audio) + 1
            db_sess.commit()
        db_sess.commit()
    else:
        abort(404)
    return redirect('/main')


@app.route('/like/<int:audio_id>', methods=['GET', 'POST'])
@login_required
def like(audio_id):
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    audio_likers = audio.likers.split() if audio.likers else []
    audio_dislikers = audio.dislikers.split() if audio.dislikers else []
    if audio:
        if str(current_user.id) not in audio_likers:
            audio.likes += 1
            audio_likers.append(str(current_user.id))
            if str(current_user.id) in audio_dislikers:
                audio.dislikes -= 1
                del audio_dislikers[audio_dislikers.index(str(current_user.id))]
        else:
            audio.likes -= 1
            del audio_likers[audio_likers.index(str(current_user.id))]
        audio.likers = ' '.join(audio_likers)
        audio.dislikers = ' '.join(audio_dislikers)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/main')


@app.route('/dislike/<int:audio_id>', methods=['GET', 'POST'])
@login_required
def dislike(audio_id):
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    audio_likers = audio.likers.split() if audio.likers else []
    audio_dislikers = audio.dislikers.split() if audio.dislikers else []
    if audio:
        if str(current_user.id) not in audio_dislikers:
            audio.dislikes += 1
            audio_dislikers.append(str(current_user.id))
            if str(current_user.id) in audio_likers:
                audio.likes -= 1
                del audio_likers[audio_likers.index(str(current_user.id))]
        else:
            audio.dislikes -= 1
            del audio_dislikers[audio_dislikers.index(str(current_user.id))]
        audio.likers = ' '.join(audio_likers)
        audio.dislikers = ' '.join(audio_dislikers)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/main')


if __name__ == '__main__':
    main()
