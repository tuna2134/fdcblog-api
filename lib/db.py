from sanic import Request

from functools import wraps


def get_collection(name: str):
    def decorator(func: callable):
        @wraps(func)
        async def decorated_func(request: Request, *args, **kwargs):
            return await func(request, request.app.get_collection(name), *args, **kwargs)
        return decorated_func
    return decorator
