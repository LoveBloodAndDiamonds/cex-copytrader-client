from fastapi import APIRouter, Response
from starlette.requests import Request

from app.configuration import logger, config
from app.managers import UnifiedServiceManager
from ..models import UserSettings

router = APIRouter()


@router.post("/userr_settings")
def handle_trader_settings_update(request: Request, data: UserSettings) -> Response:
    """
    Функция принимает запрос с информацией о трейдере.
    """
    # Проверка на то что запрос пришел с master сервера
    if request.client.host != config.MASTER_SERVER_HOST:
        logger.warning(f"User settings event from unknown host: {request.client.host}:{request.client.port}")
        return Response(status_code=403)

    UnifiedServiceManager.on_user_settings_update(data)
