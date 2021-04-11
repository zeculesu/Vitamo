from flask import jsonify
from flask_restful import Resource, abort

from .parser import user_put_parser, user_add_parser
from .. import db_session
from ..models.users import User


def handle_user_id(user_id, session):
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')
    return user


class UserResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = handle_user_id(user_id, session)
        return jsonify({'user': user.to_dict(only=User.serialize_fields, users_in_chats=False)})

    def put(self, user_id):
        session = db_session.create_session()
        user = handle_user_id(user_id, session)
        args = user_put_parser.parse_args()
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
    user_fields = ('id', 'email', 'username', 'description',
                   'logo', 'chats', 'created_date')

    def get(self):
        session = db_session.create_session()
        users = [user.to_dict(only=self.user_fields, users_in_chats=False)
                 for user in session.query(User).all()]
        return jsonify({'users': users})

    @staticmethod
    def post():
        session = db_session.create_session()
        args = user_add_parser.parse_args()
        if session.query(User).filter(User.email == args['email']).first():
            abort(400, message=f'User with email {args["email"]} already exists')
        password = args.pop('password')
        user = User(**args)
        user.set_password(password)
        session.add(user)
        session.commit()
        return jsonify({'message': 'OK'})