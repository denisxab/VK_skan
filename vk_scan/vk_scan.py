from asyncio import sleep, gather
from re import match
from time import time
from typing import Tuple

from httpx import AsyncClient
from logsmal import logger
from sqlalchemy import insert, select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from database import SQL, SqlScript, SqlLite
from helpful import sync_http_get, offset_array
from model import GroupsVk, UsersVk


class SearchUserInGroup:
    # Сколько юзеров с ошибкой
    user_false = 0
    all_id: list = []

    def __init__(
            self,
            token_vk: str,
            group_name: str,
            versionApi: str,
            limit_get_user_group: int = 0,
            count_coroutine: int = 5,
    ):
        """
        :param token_vk: Токен VK
        :param group_name: ID группы
        :param limit_get_user_group: Сколько максимум взять  участников (по умолчанию все)
        :param versionApi: Версия VK API
        """
        self.token: str = token_vk
        self.name_group: str = [
            _name
            for _name in match('https://vk.com/([\w\d_]+)|([\w\d_]+)', group_name).groups()
            if _name
        ][0]
        self.version_api: str = versionApi
        self.count_user: int = self._get_cont_user_group() if not limit_get_user_group else limit_get_user_group
        self.count_coroutine = count_coroutine
        self.count_offset_thread = offset_array(self.count_user, self.count_coroutine)

    def _get_cont_user_group(self) -> int:
        """
        Получить количество подписчиков в группе
        """
        response: dict = sync_http_get(
            'https://api.vk.com/method/groups.getMembers',
            params={
                "access_token": self.token,
                'v': self.version_api,
                "group_id": self.name_group,
                'count': 1,
                'offset': 1,
            }
        )

        if response.get('error'):
            if response['error']["error_code"] == 125:
                raise ValueError("Неправильный id группы")
            if response['error']["error_code"] == 5:
                raise ValueError("У вас Неверный Токен ID")
            raise ValueError(response)
        return response['response']['count']

    @SQL.get_session_decor
    async def search(self, _session: AsyncSession):

        response: GroupsVk = await SqlScript.set_row_if_not_unique(
            sql_get=select(GroupsVk).where(GroupsVk.name_group == self.name_group),
            sql_set=GroupsVk(name_group=self.name_group),
            _session=_session
        )

        tasks = []
        time_sleep_thread = 0
        for x in range(self.count_coroutine):
            time_sleep_thread += 0.3
            tasks.append(
                self.scan_group(
                    time_sleep_thread,
                    self.count_offset_thread[x],
                    self.name_group,
                    self.token,
                    self.version_api,
                    groups_id=response.id
                )
            )

        await gather(*tasks)

    @staticmethod
    @SQL.get_session_decor
    async def scan_group(
            time_sleep_thread: float,
            padding: Tuple[int, int],
            group_name: str,
            token_vk: str,
            v: str,
            groups_id: int,
            _session: AsyncSession
    ):
        """
        https://vk.com/dev/groups.getMembers - описание метода
        https://vk.com/dev/objects/user - описания фильтра

        sex = пол
        city = информация о городе, указанном на странице пользователя в разделе «Контакты». Возвращаются следующие поля:
        bdate = дата рождения
        followers_count = количество подписчиков пользователя.
        relation = семейное положение. Возможные значения:
                    1 — не женат/не замужем;
                    2 — есть друг/есть подруга;
                    3 — помолвлен/помолвлена;
                    4 — женат/замужем;
                    5 — всё сложно;
                    6 — в активном поиске;
                    7 — влюблён/влюблена;
                    8 — в гражданском браке;
                    0 — не указано.
        can_write_private_message = информация о том, может ли текущий пользователь отправить личное сообщение. Возможные значения:
                    1 — может;
                    0 — не может.

        last_seen = time (integer) — время последнего посещения в формате Unixtime.
        """

        async def save_db():
            # Сохраняем данные в БД
            if len(all_id) >= counts:
                await _session.execute(insert(UsersVk, prefixes=[SqlLite.prefixes_ignore_insert]), all_id)
                await _session.commit()
                logger.info(f'{time_sleep_thread}', 'Записывает данные в БД')
                # Если данные записанные в БД, то отчищаем массив
                all_id.clear()

        counts = 1000
        offset = padding[0]
        all_id = []

        while offset <= padding[1]:
            async with AsyncClient(timeout=20) as session:
                responseGet = await session.get('https://api.vk.com/method/groups.getMembers', params={
                    "access_token": token_vk,
                    'v': v,
                    "group_id": group_name,
                    'count': counts,
                    'offset': offset,
                    'fields': 'sex,city,bdate,followers_count,relation,can_write_private_message,last_seen'
                })
                responseJson = responseGet.json()

            logger.info(f'{padding[1] - offset}', 'Отступы')

            offset += counts
            try:
                for i in responseJson['response']['items']:
                    try:
                        all_id.append(
                            {
                                'user_id': i['id'],  # id пользователя
                                'sex': i['sex'],  # Пол
                                'bdata': int(i['bdate'].split('.')[2]),  # Дата рождения
                                'city': i['city']['id'],  # Город
                                'cwpm': i['can_write_private_message'],  # Возможность писать сообщения
                                'followers': i['followers_count'],  # Количество подписчиков
                                'relation': i['relation'],  # Семенное положение
                                'last_seen': i["last_seen"]["time"],  # Дата последнего посещения ВК
                                'groups_id': groups_id,
                            }
                        )

                    except (IndexError, KeyError):
                        SearchUserInGroup.user_false += 1  # Количество пользователи которые не имели таких полей
            except KeyError:
                if responseJson["error"]["error_code"] == 6:
                    print("Слишком много запросов в секунду, данные не полученные с сервера, увеличите задержку")
                    # Проходим заново
                    offset -= counts
                    logger.warning(f'{padding[1] - offset}', ' Проходим заново')
                    await sleep(time_sleep_thread)
                else:
                    print(responseJson["error"]["error_code"])

            await save_db()
            await sleep(time_sleep_thread)

    @staticmethod
    @SQL.get_session_decor
    async def show_search(_session: AsyncSession):
        now = time() - 604800

        sql_ = select(UsersVk).where(
            (UsersVk.sex == 1) &
            (UsersVk.bdata.between(1999, 2001)) &
            (UsersVk.city == 2) &
            (UsersVk.cwpm == 1) &
            (UsersVk.followers <= 800) &
            ((UsersVk.relation == 0) | (UsersVk.relation == 6) | (UsersVk.relation == 1)) &
            (UsersVk.last_seen >= now)
        )

        res: ChunkedIteratorResult = await _session.execute(sql_)
        return res.fetchall()
