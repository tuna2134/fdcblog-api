from sanic import Blueprint
from lib import mysql


bp = Blueprint("status", url_prefix="/shikimori")


def json(data: Optional[Any] = None, *, message: Optional[str] = None, status: int = 200):
    return response.json({
        "status": status,
        "message": message,
        "data": data
    }, status=status)


@bp.get("/status")
@mysql
async def status(request, cursor):
    await cursor.execute("SELECT * FROM Status;")
    return json([{"time": time, "cpu": cpu, "memory": memory, "disk": disk, "ping": ping}
                 for time, cpu, memory, disk, ping in await cursor.fetchall()]
