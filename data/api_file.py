from flask import jsonify
from flask_restful import reqparse, abort, Resource

from data import db_session
from data.audio import Audio
from data.users import User


parser = reqparse.RequestParser()
parser.add_argument('user_surname', required=True)
parser.add_argument('user_name', required=True)
parser.add_argument('user_password', required=True)
parser.add_argument('user_email', required=True, type=bool)
parser.add_argument('user_role', required=True, type=bool)
parser.add_argument('user_age', required=True, type=int)


def abort_if_not_found(thing_id, cls):
    session = db_session.create_session()
    thing = session.query(cls).get(thing_id)
    if not thing:
        abort(404, message=f"{cls.__name__} {thing_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_not_found(user_id, User)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('surname', 'name', 'email', 'role', 'age'))})

    def delete(self, user_id):
        abort_if_not_found(user_id, User)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'SUCCESS': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['user_surname'],
            name=args['user_name'],
            role=args['user_role'],
            email=args['user_email'],
            age=args['user_age']
        )
        user.set_password(args['user_password'])
        session.add(user)
        session.commit()
        return jsonify({'SUCCESS': 'OK'})


class AudioListResource(Resource):
    def get(self):
        session = db_session.create_session()
        audios = session.query(Audio).all()
        return jsonify({'audios': [item.to_dict() for item in audios]})


class AudioResource(Resource):
    def get(self, audio_id):
        abort_if_not_found(audio_id, Audio)
        session = db_session.create_session()
        audio = session.query(Audio).get(audio_id)
        return jsonify({'audio': audio.to_dict()})

    def delete(self, audio_id):
        abort_if_not_found(audio_id, Audio)
        session = db_session.create_session()
        audio = session.query(Audio).get(audio_id)
        session.delete(audio)
        session.commit()
        return jsonify({'SUCCESS': 'OK'})
