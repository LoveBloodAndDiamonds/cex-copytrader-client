import time
import requests

import binance.lib.utils  # Импорт только модуля utils до основной библиотеки

from app.configuration import logger

# Monkey patch of binance timestamp lib
try:
    timestamp_offset: float = requests.get(
        url="https://fapi.binance.com/fapi/v1/time"
    ).json()["serverTime"] - int(time.time() * 1000)

    def _patched_get_timestamp() -> float:
        return int(time.time() * 1000 + timestamp_offset)

    binance.lib.utils.get_timestamp = _patched_get_timestamp
except Exception as e:
    logger.error(f"Error while monkey patching binance timestamp offset: {e}")
