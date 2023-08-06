"""User authentication with the ObjectRocket API."""
import functools

from flask import request
from flask import g
from flask.ext.restful import abort
from flask.ext.restful import Resource

from objectrocket import Client


def objectrocket_authentication(func):
    """RESTful middleware for authentication with ObjectRocket APIv2."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            # Extract and evaluate credentials.
            token = request.headers.get('x-auth-token', None)
            if token is None:
                raise ValueError('No credentials provided.')

            # Verify token with APIv2.
            user_data = Client().auth._verify(token)
            if user_data is None:
                raise ValueError('Invalid credentails provided.')

            # Bind the user object for the duration of this request.
            g.user = ObjectRocketUser(user_data=user_data, token=token)
            g.instances = []  # Cache of the users instances for this request.

        except ValueError as ex:
            abort(401, message=str(ex))

        return func(*args, **kwargs)

    return wrapped


class ObjectRocketResource(Resource):

    method_decorators = [objectrocket_authentication]


class ObjectRocketUser(object):

    def __init__(self, user_data, token):
        uid = user_data.pop('_id', None) or user_data.pop('id', None)
        login = user_data.pop('login', None)
        if not uid or not login:
            raise ValueError(
                'A user ID and login is required for ObjectRocket users.'
            )

        self.id = uid
        self.login = login
        self.token = token
        self.__client = Client()
        self.__client.auth._token = token

        for key, val in user_data.items():
            if key not in ['id', 'login', 'token', 'client']:
                setattr(self, key, val)

    @property
    def client(self):
        """This users ObjectRocket client object."""
        return self.__client
