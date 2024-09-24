import requests

from app.schemas.types import M
from app.schemas.exceptions import MasterServerConnectionError
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


def find_unique_positions(positions_1: list[dict], positions_2: list[dict]):
    list1_dict = {(item['symbol'], item['positionSide'], int(item['positionAmt'] > 0)): item for item in positions_1}
    list2_dict = {(item['symbol'], item['positionSide'], int(item['positionAmt'] > 0)): item for item in positions_2}

    return [item for item in list1_dict if item not in list2_dict]
