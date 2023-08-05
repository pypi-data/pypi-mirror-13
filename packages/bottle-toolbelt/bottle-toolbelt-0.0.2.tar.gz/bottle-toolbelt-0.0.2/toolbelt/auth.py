import os

from bottle import request


def dynamic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

user_path = os.getenv('VALIDATE_TOKEN')
validate_token = dynamic_import(user_path)


def token_authentication(callback):
    def wrapper(*args, **kwargs):
        # Authorization: Token abc
        token = request.headers.get('Authorization', '') # Token abc
        try:
            token = token.split()[1].strip()
            user = validate_token(token)
            request.current_user = user
        except IndexError:
            return error_response('Unauthorized. What is the token?', 499)
        except User.DoesNotExist:
            return error_response('Unauthorized. Bad token.', 401)
        body = callback(*args, **kwargs)
        return body
    return wrapper
