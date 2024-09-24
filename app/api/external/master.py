__all__ = ["router", ]

from fastapi import APIRouter, Response
from starlette.requests import Request

from app.configuration import logger, config
from app.manager import ServiceManager
from app.schemas.models import TraderSettings, UserSettings

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

    ServiceManager.on_trader_settings_update(update)


@router.post("/user_settings")
async def handle_trader_settings_update(request: Request) -> Response:
    """
    Функция принимает запрос с информацией о трейдере.
    """
    try:
        update: UserSettings = UserSettings(**(await request.json()))
    except Exception:  # noqa
        return Response(status_code=400)

    # Проверка на то что запрос пришел с master сервера
    if request.client.host != config.MASTER_SERVER_HOST:
        logger.warning(f"Event({update}) from unknown host: {request.client.host}:{request.client.port}")
        return Response(status_code=403)

    ServiceManager.on_user_settings_update(update)
