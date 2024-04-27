import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Images(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer)
    photo_id = sqlalchemy.Column(sqlalchemy.Integer)
    link = sqlalchemy.Column(sqlalchemy.String)
