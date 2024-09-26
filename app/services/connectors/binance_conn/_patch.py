"""
This update repairs exception what raises whenerver we launch async FastAPI aplication and ThreadedWebsocketManager:
И ГОРИТЕ В АДУ СОЗДАТЕЛИ python-binance, за то что затащили асинхронность в THREADED WebsocketManager

--
Issue:
https://github.com/sammchardy/python-binance/issues/1354
I don't know what is your situation exactly, but the problem described by me above could be solved by replacing
self._loop: asyncio.AbstractEventLoop = get_loop()
to
self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
in file https://github.com/sammchardy/python-binance/blob/master/binance/threaded_stream.py
--

Exception in thread Thread-5:
Traceback (most recent call last):
  File "/usr/lib/python3.11/threading.py", line 1038, in _bootstrap_inner
    self.run()
  File "/root/.cache/pypoetry/virtualenvs/cex-copytrader-master-2HKd35j_-py3.11/lib/python3.11/site-packages/
  binance/threaded_stream.py", line 59, in run
    self._loop.run_until_complete(self.socket_listener())
  File "/usr/lib/python3.11/asyncio/base_events.py", line 626, in run_until_complete
    self._check_running()
  File "/usr/lib/python3.11/asyncio/base_events.py", line 586, in _check_running
    raise RuntimeError('This event loop is already running')
RuntimeError: This event loop is already running
/usr/lib/python3.11/threading.py:1040: RuntimeWarning: coroutine 'ThreadedApiManager.socket_listener' was never awaited
  self._invoke_excepthook(self)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
"""

import asyncio
from threading import Thread
import time
from typing import Optional, Dict, Any, Callable

from binance import AsyncClient, BinanceSocketManager
from binance.helpers import get_loop


class _PatchedThreadedApiManager(Thread):

    def __init__(
            self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
            requests_params: Optional[Dict[str, Any]] = None, tld: str = 'com',
            testnet: bool = False, session_params: Optional[Dict[str, Any]] = None
    ):
        """Initialise the BinanceSocketManager

        """
        super().__init__()
        self._loop: asyncio.AbstractEventLoop = get_loop()
        self._client: Optional[AsyncClient] = None
        self._running: bool = True
        self._socket_running: Dict[str, bool] = {}
        self._client_params = {
            'api_key': api_key,
            'api_secret': api_secret,
            'requests_params': requests_params,
            'tld': tld,
            'testnet': testnet,
            'session_params': session_params,
        }

    async def _before_socket_listener_start(self):
        ...

    async def socket_listener(self):
        self._client = await AsyncClient.create(loop=self._loop, **self._client_params)
        await self._before_socket_listener_start()
        while self._running:
            await asyncio.sleep(0.2)
        while self._socket_running:
            await asyncio.sleep(0.2)

    async def start_listener(self, socket, path: str, callback):
        async with socket as s:
            while self._socket_running[path]:
                try:
                    msg = await asyncio.wait_for(s.recv(), 3)
                except asyncio.TimeoutError:
                    ...
                    continue
                else:
                    if not msg:
                        continue
                    callback(msg)
        del self._socket_running[path]

    def run(self):
        self._loop.create_task(self.socket_listener())
        # self._loop.run_until_complete(self.socket_listener())

    def stop_socket(self, socket_name):
        if socket_name in self._socket_running:
            self._socket_running[socket_name] = False

    async def stop_client(self):
        if not self._client:
            return
        await self._client.close_connection()

    def stop(self):
        if not self._running:
            return
        self._running = False
        self._loop.call_soon(asyncio.create_task, self.stop_client())
        for socket_name in self._socket_running.keys():
            self._socket_running[socket_name] = False


class PatchedThreadedWebsocketManager(_PatchedThreadedApiManager):

    def __init__(
            self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
            requests_params: Optional[Dict[str, Any]] = None, tld: str = 'com',
            testnet: bool = False, session_params: Optional[Dict[str, Any]] = None
    ):
        super().__init__(api_key, api_secret, requests_params, tld, testnet, session_params)
        self._bsm: Optional[BinanceSocketManager] = None

    async def _before_socket_listener_start(self):
        assert self._client
        self._bsm = BinanceSocketManager(client=self._client)

    def _start_async_socket(
            self, callback: Callable, socket_name: str, params: Dict[str, Any], path: Optional[str] = None
    ) -> str:
        while not self._bsm:
            time.sleep(0.1)
        socket = getattr(self._bsm, socket_name)(**params)
        socket_path: str = path or socket._path  # noqa
        self._socket_running[socket_path] = True
        self._loop.call_soon_threadsafe(asyncio.create_task, self.start_listener(socket, socket_path, callback))
        return socket_path

    def start_futures_user_socket(self, callback: Callable) -> str:
        return self._start_async_socket(
            callback=callback,
            socket_name='futures_user_socket',
            params={}
        )
