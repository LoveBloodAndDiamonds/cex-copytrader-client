from dataclasses import dataclass


@dataclass
class MasterServerConnectionError(ConnectionError):
    status_code: int
    response_text: str
