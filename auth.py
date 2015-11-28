from flask import request
from functools import wraps
from errors import InvalidUsage


def _check_auth(username, password):
    return username == 'admin' and password == 'admin'


def _authenticate():
    raise InvalidUsage('Not authorized', status_code=401)


# authorization decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return _authenticate()
        return f(*args, **kwargs)
    return decorated
