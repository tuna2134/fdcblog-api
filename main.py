from sanic import Sanic, response
from sanic_ext import Extend
import psutil
from misaka import Markdown, HtmlRenderer

from typing import Optional, Any

from os import getenv
from functools import wraps
import string
import random
import multiprocessing

from lib.backend import Backend
from lib.cors import add_cors_headers


app = Backend("app")
Extend(app)
app.register_middleware(add_cors_headers, "response")
workers = multiprocessing.cpu_count()

blog_collection = app.get_collection("blogs")
rndr = HtmlRenderer()
md = Markdown(rndr)

def json(data: Optional[Any] = None, *, message: Optional[str] = None, status: int = 200):
    return response.json({
        "status": status,
        "message": message,
        "data": data
    }, status=status)

def authorized(func):
    @wraps(func)
    async def decorated_func(request, *args, **kwargs):
        if request.token == getenv("password"):
            return await func(request, *args, **kwargs)
        else:
            return json(message="Password is invalid", status=403)
    return decorated_func

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


@app.get("/")
async def main(request):
    return json(message="hello")

@app.post("/blogs")
@authorized
async def add_blog(request):
    data = request.json
    _id = randomname(20)
    await blog_collection.insert_one({
        "title": data["title"],
        "description": data["description"],
        "content": md(data["content"]),
        "id": _id
    })
    return json({
        "id": _id
    }, message="added")

@app.get("/blogs")
async def get_blogs(request):
    cursor = blog_collection.find(None, {"_id": False})
    return json(await cursor.to_list(length=20))

@app.get("/blogs/<_id>")
async def get_blog(request, _id):
    data = await blog_collection.find_one(
        {"id": _id},
        {"_id": False}
    )
    if data is None:
        return json(message="Not found", status=404)
    return json(data)

@app.get("/status")
async def status(request):
    return json({
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("./").percent,
        "workers": workers
    })


if __name__ == "__main__":
    app.run("0.0.0.0", 8080, fast=True)
