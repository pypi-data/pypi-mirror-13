import os

from bottle import request


User = os.getenv('USER')


def token_authentication(callback):
    def wrapper(*args, **kwargs):
        # Authorization: Token abc
        token = request.headers.get('Authorization', '') # Token abc
        try:
            token = token.split()[1].strip()
            user = User.objects.get(api_key=token)
            request.current_user = user
        except IndexError:
            return error_response('Unauthorized. What is the token?', 499)
        except User.DoesNotExist:
            return error_response('Unauthorized. Bad token.', 401)
        body = callback(*args, **kwargs)
        return body
    return wrapper
