from fastapi import FastAPI
import uvicorn

from .api.external import user_router, trader_router
from .api.internal import register_admin_routes
from .managers import UnifiedServiceManager
from .configuration import logger, config
from .database import Database

# Main fastapi obj
app = FastAPI()


def startup() -> None:
    """ Startup function """
    logger.info("Application startup!")
    logger.info(f"Uvicorn running at http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info(f"Admin panel running at http://{config.SERVER_HOST}:{config.SERVER_PORT}/admin")

    # Create keys model if not exists
    Database.keys_repo.create_if_not_exists()

    # Register external routers
    app.include_router(user_router)
    app.include_router(trader_router)

    # Register internal routes
    register_admin_routes(app)

    # Run some background tasks
    UnifiedServiceManager.run_tasks()


def shutdown() -> None:
    """ Shutdown function """
    logger.info("Application shutdown!")


try:
    startup()

    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT, log_level="error")
except Exception as e:
    logger.exception(f"Unexcepted exception at top level: {e}")
finally:
    shutdown()
