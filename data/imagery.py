import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Imagery(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'imagery'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer)
    photo_id = sqlalchemy.Column(sqlalchemy.Integer)
    description = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String)
