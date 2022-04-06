import datetime
import sqlalchemy
from sqlalchemy import orm
from . import users


from .db_session import SqlAlchemyBase


class Audio(SqlAlchemyBase):
    __tablename__ = 'audio'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publisher = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    publish_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Audio> {self.id} {self.author} {self.name}'