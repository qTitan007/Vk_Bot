import flask
from flask import jsonify

from data import db_session
from data.imagery import Imagery
from data.images import Images
from data.quote import Quote

blueprint = flask.Blueprint('quote_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/get_quote')
def get_quote():
    session = db_session.create_session()
    quote = session.query(Quote).all()
    return jsonify(
        {'quote': [item.to_dict(only=('id', 'value')) for item in quote]}
    )


@blueprint.route('/api/get_images')
def get_images():
    session = db_session.create_session()
    images = session.query(Images).all()
    return jsonify(
        {'images': [item.to_dict(only=('id', 'owner_id', 'photo_id')) for item in images]}
    )


@blueprint.route('/api/get_imagery')
def get_imagery():
    session = db_session.create_session()
    imagery = session.query(Imagery).all()
    return jsonify(
        {'imagery': [item.to_dict(only=('id', 'owner_id', 'photo_id', 'description')) for item in imagery]}
    )
