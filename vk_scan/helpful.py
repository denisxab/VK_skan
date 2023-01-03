from asyncio import run
from json import load
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from mg_sql.sql_async.base import SQL

from model_db import TUserVk

#
################################################################
#


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
#
################################################################
#


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
#
################################################################
#


def sync_http_get(url: str, params: dict[str, Any]):
    async def __self():
        async with AsyncClient() as session:
            responseGet = await session.get(url, params=params)
            return responseGet.json()
    return run(__self())
#
################################################################
#


@SQL.get_session_decor
async def show_necessary_users(name_group: str, skip_first: int = 0, _session: AsyncSession = None) -> list[TUserVk]:
    """
    Показать подходящих пользовательниц

    name_group: Имя группы
    """
    sql_ = f"""
    select uv.* from users_vk uv 
    join group_vk gv on gv.name_group ='{name_group}' and gv.id=uv.groups_id
    where 
        -- Девушки
        sex=1
        -- Последнее посещения не более 1 недели
        and time_add-last_seen <= 604800
        -- Из СПБ
        and city=2
        -- Можно писать
        and cwpm=1
        -- Менее 800 подписчиков
        and followers<=800
        -- Свободный статус
        and relation in (0,1,6)
        -- От 18-30 лет
        and bdata BETWEEN 1993 and 2004 
    LIMIT -1 OFFSET {skip_first}
    --ORDER by bdata desc; 
    """
    res = await SQL.read_execute_raw_sql(_session, raw_sql=sql_)
    return res
#
################################################################
#


@SQL.get_session_decor
async def show_like_users(_session: AsyncSession) -> list[TUserVk]:
    """
    Показать отлайканых пользовательниц
    """
    sql_ = """
    select uv.*
    FROM like_user lu 
    join users_vk uv on uv.user_id=lu.user_id 
    order by lu.id 
    """
    res = await SQL.read_execute_raw_sql(_session, raw_sql=sql_)
    return res
