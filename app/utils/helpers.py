import requests

from app.schemas.types import M
from app.schemas.exceptions import MasterServerConnectionError
from app.schemas.models import UserBalanceUpdate
from app.configuration import config


def request_model(endpoint: str, model: M) -> type[M]:
    """
    Function requests model from master server.
    :param endpoint: Enpoint URL
    :param model: Model what we wanna request
    :return: requested BaseModel
    """
    response: requests.Response = requests.get(
        url=f"http://{config.MASTER_SERVER_HOST}:{config.MASTER_SERVER_PORT}/{config.VERSION}/{endpoint}")

    if response.status_code == 200:
        return model(**response.json())
    raise MasterServerConnectionError(status_code=response.status_code, response_text=response.text)
