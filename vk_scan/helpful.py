from asyncio import run
from json import load
from typing import Dict, Any

from httpx import AsyncClient


def get_my_password(path_config: str) -> Dict[str, str]:
    """
    Получить токен username и пароль
    """
    try:
        with open(path_config, 'r') as _f:
            read = load(_f)
            if len(read) == 3:
                return read
            else:
                raise IOError("Неправильный формат ввода пароля")

    except FileNotFoundError:
        raise IOError(f"Отсутствует фал {path_config}")


def sync_http_get(url: str, params: dict[str, Any]):
    async def __self():
        async with AsyncClient() as session:
            responseGet = await session.get(url, params=params)
            return responseGet.json()

    return run(__self())
