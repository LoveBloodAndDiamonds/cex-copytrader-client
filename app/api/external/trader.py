from fastapi import APIRouter, Response
from starlette.requests import Request

from app.configuration import logger, config
from app.managers import UnifiedServiceManager
from ..models import TraderSettings

router = APIRouter()


@router.post("/trader_settings")
async def handle_trader_settings_update(request: Request) -> Response:
    """
    Функция принимает запрос с информацией о трейдере.
    """
    try:
        update: TraderSettings = TraderSettings(**(await request.json()))
    except Exception:  # noqa
        return Response(status_code=400)

    # Проверка на то что запрос пришел с master сервера
    if request.client.host != config.MASTER_SERVER_HOST:
        logger.warning(f"Update({update}) from unknown host: {request.client.host}:{request.client.port}")
        return Response(status_code=403)

    UnifiedServiceManager.on_trader_settings_update(update)
