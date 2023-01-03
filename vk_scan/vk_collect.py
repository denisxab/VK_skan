from asyncio import sleep, gather
from re import match
from time import time
from typing import Tuple
from httpx import AsyncClient
from logsmal import logger
from sqlalchemy.ext.asyncio import AsyncSession
from mg_sql.sql_async.base import SQL
from helpful import sync_http_get, offset_array


class CollectUserFomGroup:
    # Сколько юзеров с ошибкой
    user_false = 0

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
        # Токен
        self.token: str = token_vk
        # Имя группы
        self.name_group: str = [
            _name
            for _name in match('https://vk.com/([\w\d_]+)|([\w\d_]+)', group_name).groups()
            if _name
        ][0]
        # Версия API
        self.version_api: str = versionApi
        # Сколько пользователей нужно получить из группы
        self.count_user: int = self._get_cont_user_group() if not limit_get_user_group else limit_get_user_group
        # Сколько сделать асинхронных карутин
        self.count_coroutine = count_coroutine
        # Отступы для карутин
        self._count_offset_thread = offset_array(self.count_user, self.count_coroutine)

    async def run(self):
        """
        Начать сбор информации из группы, параллельно в нескольких карутинах
        """
        # Создаем группу в БД
        groups_id=await self._AddGroupIfNotExist(self.name_group)
        # Создаем асинхронные задачи
        tasks = []
        time_sleep_thread = 0
        for x in range(self.count_coroutine):
            # Разная задержка для каждой картуины
            time_sleep_thread += 0.3
            tasks.append(
                self.coroutine_collect(
                    time_sleep_thread,
                    self._count_offset_thread[x],
                    self.name_group,
                    self.token,
                    self.version_api,
                    groups_id=groups_id
                )
            )
        # Запускаем асинхронные задачи
        await gather(*tasks)

    @staticmethod
    @SQL.get_session_decor
    async def coroutine_collect(
            time_sleep_thread: float,
            padding: Tuple[int, int],
            group_name: str,
            token_vk: str,
            v: str,
            groups_id: int,
            _session: AsyncSession
    ):
        """
        Зада для каждой карутины по сбору данных в группе
        
        https://vk.com/dev/groups.getMembers - описание метода
        https://vk.com/dev/objects/user - описания фильтра

        sex = пол 
            - 2 - Муж
            - 1 - Женский 
            - 0 - скрыт
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
            await SQL.write_execute_raw_sql(_session, raw_sql="""
            insert or REPLACE into users_vk (user_id,groups_id,sex,bdata,city,cwpm,followers,relation,last_seen,time_add) values {I};
            """.format(I=','.join(
                    f"({x['user_id']},{x['groups_id']},{x['sex']},{x['bdata']},{x['city']},{x['cwpm']},{x['followers']},{x['relation']},{x['last_seen']},{int(time())})" 
                    for x in all_id
                )
            ))
            logger.info(f'{time_sleep_thread}', ['Записывает данные в БД'])
            # Если данные записанные в БД, то отчищаем массив
            all_id.clear()

        # Сколько можно получать пользователей за один раз
        counts = 1000
        # Оступы для получения у каждой карутины
        offset = padding[0]
        # Список с пользователями
        all_id = []

        while offset <= padding[1]:
            # Получаем список пользователей из группы
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
            logger.info(f'{padding[1] - offset}', ['Отступы'])
            # Отмечаем о том что получены пользователи
            offset += counts
            try:
                # Парсим ответ
                for i in responseJson['response']['items']:
                    try:
                        bdate=int(i['bdate'].split('.')[2])
                        #@@ Девушки из СПБ@@#
                        if i['sex'] == 1 and i['city']['id'] == 2:
                            all_id.append(
                                {
                                    'user_id': i['id'],  # id пользователя
                                    'sex': i['sex'],  # Пол
                                    'bdata': bdate,  # Дата рождения
                                    'city': i['city']['id'],  # Город
                                    'cwpm': i['can_write_private_message'],  # Возможность писать сообщения
                                    'followers': i['followers_count'],  # Количество подписчиков
                                    'relation': i['relation'],  # Семенное положение
                                    'last_seen': i["last_seen"]["time"],  # Дата последнего посещения ВК
                                    'groups_id': groups_id,
                                }
                            )
                        else: # 1573644
                            CollectUserFomGroup.user_false += 1  # Количество пользователи которые не имели таких полей
                    except (IndexError, KeyError):
                        CollectUserFomGroup.user_false += 1  # Количество пользователи которые не имели таких полей
            except KeyError as e:
                if responseJson["error"]["error_code"] == 6:
                    print("Слишком много запросов в секунду, данные не полученные с сервера, увеличите задержку")
                    # Проходим заново
                    offset -= counts
                    logger.warning(f'{padding[1] - offset}', ' Проходим заново')
                    await sleep(time_sleep_thread)
                else:
                    print(responseJson["error"]["error_code"])
            #
            if len(all_id) >= counts:
                await save_db()
            await sleep(time_sleep_thread)
        #
        if len(all_id) > 0:
            await save_db()
        logger.success(f'{time_sleep_thread}',['Карутина завершила работу'])
        
    ########################################################################################
    # Утилиты
    ########################################################################################
    def _get_cont_user_group(self) -> int:
        """
        Получить количество подписчиков в группе
        """
        # Получаем количество всех пользователей в группе 
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
        # Обработка ошибок
        if response.get('error'):
            if response['error']["error_code"] == 125:
                raise ValueError("Неправильный id группы")
            if response['error']["error_code"] == 5:
                raise ValueError("У вас Неверный Токен ID")
            raise ValueError(response)
        return response['response']['count']

    @staticmethod
    @SQL.get_session_decor
    async def _AddGroupIfNotExist(name_group:str,_session: AsyncSession)->int:
        """
        Добавить группу в БД если её нет.
        
        return: Id группы
        """
        # Проверяем наличие группы группы
        sql = """
        select id from group_vk gv where name_group =:name_group;
        """
        # Получаем ID группы
        res = await SQL.read_execute_raw_sql(_session, raw_sql=sql, params={"name_group":name_group})    
        # Если группы нет то создаем новую группу
        if not res:
            await SQL.write_execute_raw_sql(_session, raw_sql="""
            INSERT into group_vk (name_group) values (:name_group);
            """,params={"name_group":name_group})
            logger.info(f"Группа создана: {name_group}")
            # Получаем ID новой группы
            res = await SQL.read_execute_raw_sql(_session, raw_sql=sql, params={"name_group":name_group})    
        #  Id группы
        return res[0]['id']


