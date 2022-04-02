from asyncio import run
from json import load
from typing import Dict, Any

from httpx import AsyncClient


def offset_array(countItem, countThread) -> list[tuple[int, int]]:
    """
    >>> offset_array(998, 4)
    [(0, 249), (249, 498), (498, 747), (747, 998)]
    """

    mid = countItem // countThread
    start: int = 0
    end: int = mid

    res: list[tuple[int, int]] = []
    for x in range(0, countThread - 1):
        res.append((start, end))
        start = end
        end += mid
    else:
        res.append((start, countItem))

    return res


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
