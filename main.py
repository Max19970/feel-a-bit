import os

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename
from flask_restful import Api

import datetime as dt
from mutagen.mp3 import MP3

from forms.user_forms import RegisterForm, LoginForm, EditInfoForm
from forms.audio_forms import PublishForm
from data.users import User
from data.audio import Audio
from data import db_session, api_file


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
roles = {'0': 'Администратор', '1': 'Модератор',
         '2': 'Слушатель', '3': 'Музыкант'}


def main():
    db_session.global_init("db/dataB.db")
    api.add_resource(api_file.UserListResource, '/api/users')
    api.add_resource(api_file.UserResource, '/api/users/<int:user_id>')
    api.add_resource(api_file.AudioListResource, '/api/audios')
    api.add_resource(api_file.AudioResource, '/api/audios/<int:audio_id>')
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
@app.route('/title')
def index():
    db_sess = db_session.create_session()
    auds = db_sess.query(Audio).all()
    auds = sorted(auds, key=lambda x: x.likes, reverse=True)
    auds = [auds[i] for i in range(5 if len(auds) >= 5 else len(auds))]
    pop_auds = []
    for audio in auds:
        pop_auds.append([audio.name, audio.file, audio.likes])
    for i in range(len(pop_auds)):
        pop_auds[i].append(i)
    return render_template('title.html', popular_audios=pop_auds, pop_len=len(pop_auds))


@app.route('/main/')
@app.route('/main/<search_value>')
def site_main(search_value=None):
    db_sess = db_session.create_session()
    audios = []
    if search_value:
        g_auds = db_sess.query(Audio).filter(Audio.name.like(f'%{search_value.lower().strip()}%')).all()
    else:
        g_auds = db_sess.query(Audio).all()
    for audio in g_auds:
        publisher = db_sess.query(User).filter(User.id == audio.publisher).first()
        publisher_name = publisher.surname + ' ' + publisher.name
        publisher_avatar = publisher.avatar_img
        audio_likers = map(int, audio.likers.split()) if audio.likers else []
        audio_dislikers = map(int, audio.dislikers.split()) if audio.dislikers else []
        comments_sum = len(audio.comments.split('✓')) if audio.comments != '' else 0
        audios.append([audio.publisher, audio.author, audio.file, audio.name,
                       audio.genre, publisher_name, audio.id, audio.likes,
                       audio.dislikes, audio_likers, audio_dislikers, publisher_avatar,
                       comments_sum])
    return render_template('main.html', audios=reversed(audios), search_value=(search_value if search_value else ''))


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
        if form.avatar_img.data:
            file = form.avatar_img.data
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/img/users_profiles/', filename))
            user.avatar_img = f'/static/img/users_profiles/{filename}'
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, mode='register')


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
    return render_template('login.html', form=form, mode='register')


@app.route('/publish',  methods=['GET', 'POST'])
@login_required
def publish():
    form = PublishForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        file = form.file.data
        file.filename = f'{len(db_sess.query(Audio).all()) + 1}.mp3'
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/audio', filename))
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
    return render_template('audio_x.html', form=form)


@app.route('/like/<data>', methods=['GET', 'POST'])
@login_required
def like(data):
    audio_id, prev_url = data.split(None, 1)
    audio_id = int(audio_id)
    prev_url = '/'.join(prev_url.split())
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
    return redirect(f'/{prev_url}')


@app.route('/dislike/<data>', methods=['GET', 'POST'])
@login_required
def dislike(data):
    audio_id, prev_url = data.split(None, 1)
    audio_id = int(audio_id)
    prev_url = '/'.join(prev_url.split())
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
    return redirect(f'/{prev_url}')


@app.route('/user/<int:user_id>')
def user_prof(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user_audios = []
    for audio in db_sess.query(Audio).filter(Audio.publisher == user_id).all():
        audio_likers = map(int, audio.likers.split()) if audio.likers else []
        audio_dislikers = map(int, audio.dislikers.split()) if audio.dislikers else []
        comments_sum = len(audio.comments.split('✓')) if audio.comments != '' else 0
        user_audios.append([audio.author, audio.file, audio.name, audio.genre, audio.id,
                            audio.likes, audio.dislikes, audio_likers, audio_dislikers,
                            comments_sum])
    for i in range(len(user_audios)):
        user_audios[i].append(i)
    user_role = roles[user.role]
    user_info = [user.surname, user.name, user_role, user.age, user.avatar_img, user.id, len(user_audios)]
    return render_template('user.html', user_info=user_info, user_audios=user_audios)


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    form = EditInfoForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user:
            form.email.data = user.email
            form.surname.data = user.surname
            form.name.data = user.name
            form.age.data = user.age
            form.role.data = user.role
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user:
            user.email = form.email.data
            if form.avatar_img.data:
                file = form.avatar_img.data
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/img/users_profiles/', filename))
                user.avatar_img = f'/static/img/users_profiles/{filename}'
            user.surname = form.surname.data
            user.name = form.name.data
            user.age = form.age.data
            user.role = form.role.data
            db_sess.commit()
            return redirect(f'/user/{user_id}')
        else:
            abort(404)
    return render_template('register.html',
                           title='Редактирование профиля',
                           form=form, mode='edit')


@app.route('/delete_audio/<data>', methods=['GET', 'POST'])
def delete_audio(data):
    audio_id, prev_url = data.split(None, 1)
    audio_id = int(audio_id)
    prev_url = '/'.join(prev_url.split())
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    if audio:
        db_sess.delete(audio)
        os.remove(audio.file)
        audios = db_sess.query(Audio).all()
        for audio in audios:
            audio.id = audios.index(audio) + 1
            db_sess.commit()
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/{prev_url}')


@app.route('/comments/<int:audio_id>')
def comments(audio_id):
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    audio_comments = []
    if audio.comments:
        for comment_data in audio.comments.split('✓'):
            commentator_id, comment_text, comment_date = comment_data.replace('[', '').replace(']', '').split('Ø', 2)
            commentator = db_sess.query(User).filter(User.id == commentator_id).first()
            comment_id = audio.comments.split('✓').index(comment_data)
            audio_comments.append([commentator, comment_text, comment_date, comment_id])
    publisher = db_sess.query(User).filter(User.id == audio.publisher).first()
    publisher_name = publisher.surname + ' ' + publisher.name
    publisher_avatar = publisher.avatar_img
    audio_likers = map(int, audio.likers.split()) if audio.likers else []
    audio_dislikers = map(int, audio.dislikers.split()) if audio.dislikers else []
    audio_info = [audio.publisher, audio.author, audio.file, audio.name,
                  audio.genre, publisher_name, audio.id, audio.likes,
                  audio.dislikes, audio_likers, audio_dislikers, publisher_avatar]
    return render_template('comments.html', audio=audio_info, audio_comments=reversed(audio_comments))


@app.route('/comment_send/<data>')
def comment_send(data):
    audio_id, commentator_id, comment_text = data.split(None, 2)
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    if audio.comments:
        audio.comments += f'✓[{commentator_id}Ø{comment_text}Ø{dt.datetime.now().strftime("%d/%m/%Y %H:%M")}]'
    else:
        audio.comments += f'[{commentator_id}Ø{comment_text}Ø{dt.datetime.now().strftime("%d/%m/%Y %H:%M")}]'
    db_sess.commit()
    return redirect(f'/comments/{audio_id}')


@app.route('/delete_comment/<data>')
def delete_comment(data):
    comment_id, audio_id = data.split()
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).filter(Audio.id == audio_id).first()
    audio_comments = audio.comments.split('✓')
    del audio_comments[int(comment_id)]
    audio.comments = '✓'.join(audio_comments)
    db_sess.commit()
    return redirect(f'/comments/{audio_id}')


if __name__ == '__main__':
    main()
