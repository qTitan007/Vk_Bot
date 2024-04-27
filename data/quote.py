import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Quote(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quote'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    value = sqlalchemy.Column(sqlalchemy.String)
