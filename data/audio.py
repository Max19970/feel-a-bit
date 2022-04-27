import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Audio(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'audio'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publisher = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    likers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dislikers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comments = sqlalchemy.Column(sqlalchemy.String, default='')
    publish_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Audio> {self.id} {self.author} {self.name}'