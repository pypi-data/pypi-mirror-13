from bottle import request, response


def p(name, default='__None__'):
    if default != '__None__':
        return request.json.get(name, default) if request.json else request.params.get(name, default)
    else:
        return request.json[name] if request.json else request.params[name]


def error_response(msg, status):
    response.status = status
    return {'error': msg}

