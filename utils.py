from flask import make_response

def allow_origin(func):
    def wrapper(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

