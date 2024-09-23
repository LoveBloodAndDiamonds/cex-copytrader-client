__all__ = ["register_admin_routes", ]

import os

import aiofiles
from fastapi import FastAPI
from sqladmin import Admin, ModelView, BaseView, expose
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.configuration import config
from app.database import Database, Keys
from app.managers import UnifiedServiceManager


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            # Validate username/password credentials
            # And update session
            request.session.update({"token": form["username"]})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


class KeysAdmin(ModelView, model=Keys):
    name = "Keys"
    name_plural = "Keys"
    can_create = False
    can_export = False
    can_view_details = False
    can_edit = True
    can_delete = False
    page_size = 1
    column_list = [Keys.exchange, Keys.api_key]

    async def after_model_change(self, data: dict, model: Keys, is_created: bool, request: Request) -> None:
        UnifiedServiceManager.on_api_keys_update(u=model)


class LogsView(BaseView):
    name = "Logs"

    @expose("/logs", methods=["GET"])
    async def logs(self, request: Request) -> HTMLResponse:
        # Reading logs files
        context: dict[str, list[str]] = {}

        for key in ["error", "info", "debug"]:
            filepath: str = f"logs/{key}.log"
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, mode='r') as file:
                    logs: list[str] = [line.strip() for line in (await file.read()).splitlines()]
                    context[key] = list(reversed(logs[-500:]))
            else:
                context[key] = [f"File {filepath} does not exists"]

        return await self.templates.TemplateResponse(request, "logs.html", context=context)


def register_admin_routes(app: FastAPI) -> None:
    # Создаем обьект-обработчик для админки
    admin: Admin = Admin(
        app=app,
        base_url="/admin",
        engine=Database.engine,
        templates_dir="app/templates",
        authentication_backend=AdminAuth(secret_key=config.CYPHER_KEY),
        title="cex-copytrader-client",
        logo_url=config.ADMIN_LOGO_URL,
    )
    # Регистрируем модели для админки
    model_views: list[type[ModelView]] = [KeysAdmin]
    for m_view in model_views:
        admin.add_model_view(m_view)
    base_views: list[type[BaseView]] = [LogsView]
    for b_view in base_views:
        admin.add_base_view(b_view)
