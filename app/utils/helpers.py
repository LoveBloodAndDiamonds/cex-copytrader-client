import requests

from app.configuration import config
from app.schemas.enums import Exchange
from app.schemas.exceptions import MasterServerConnectionError
from app.schemas.types import M, Position, Order


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


def find_unique_positions(list1: list[Position], list2: list[Position], exchange: Exchange) -> list[Position]:
    if exchange == Exchange.BINANCE:
        # Создаем множество для хранения уникальных позиций из списка 2
        set2 = {(pos['symbol'], pos['positionSide']) for pos in list2}

        # Выбираем те элементы из list1, которые отсутствуют в set2
        unique_positions = [pos for pos in list1 if (pos['symbol'], pos['positionSide']) not in set2]

        return unique_positions


def find_trader_unique_orders(trader_orders: list[Order], client_orders: list[Order]) -> list[Order]:
    client_order_ids: list[str] = [o["clientOrderId"] for o in client_orders]
    # trader_order_ids: list[str] = [o["orderId"] for o in trader_orders]

    unique_orders: list[Order] = []
    for o in trader_orders:
        if str(o["orderId"]) not in client_order_ids:
            unique_orders.append(o)

    return unique_orders


def find_client_unique_orders(client_orders: list[Order], trader_orders: list[Order]) -> list[Order]:
    # client_order_ids: list[str] = [o["clientOrderId"] for o in client_orders]
    trader_order_ids: list[str] = [str(o["orderId"]) for o in trader_orders]

    unique_orders: list[Order] = []
    for o in client_orders:
        if o["clientOrderId"] not in trader_order_ids:
            unique_orders.append(o)

    return unique_orders
