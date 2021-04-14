from flask import jsonify
from flask_restful import Resource, abort

from ... import db_session
from ...models.users import User
# from ..parsers.base import MethodParser
from ..parsers.users import *

from ..utils import handle_user_id


class UserResource(Resource):
    @staticmethod
    def get(user_id):
        session = db_session.create_session()
        user = handle_user_id(user_id, session)
        return jsonify({'user': user.to_dict()})

    def put(self, user_id):
        session = db_session.create_session()
        user = handle_user_id(user_id, session)
        parser = UserPutParser()
        args = parser.parse_args()
        if args.get('password') is not None:
            user.set_password(args.pop('password'))
        for key, val in filter(lambda x: x[1] is not None, args.items()):
            setattr(user, key, val)
        session.merge(user)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def delete(user_id):
        session = db_session.create_session()
        user = handle_user_id(user_id, session)
        session.delete(user)
        session.commit()
        return jsonify({'message': 'OK'})


class UserPublicListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        users = [user.to_dict() for user in session.query(User).all()]
        return jsonify({'users': users})

    @staticmethod
    def post():
        session = db_session.create_session()
        parser = UserAddParser()
        args = parser.parse_args()
        if session.query(User).filter(User.email == args['email']).first():
            abort(400, message=f'User with email {args["email"]} already exists')
        password = args.pop('password')
        user = User(**args)
        user.set_password(password)
        session.add(user)
        session.commit()
        return jsonify({'message': 'OK'})
