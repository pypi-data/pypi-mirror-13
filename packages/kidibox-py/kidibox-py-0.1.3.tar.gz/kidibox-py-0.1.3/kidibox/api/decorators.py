from functools import wraps


def requires_authentication(func):
    @wraps(func)
    def wrapper(client, *args, **kwargs):
        if not client.is_authenticated():
            client.authenticate()
        return func(client, *args, **kwargs)
    return wrapper
