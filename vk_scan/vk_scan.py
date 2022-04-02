from asyncio import sleep, run, gather
from re import match
from time import time
# from file.sqllite_orm_pack import SqlLiteQrm
# from file.sqllite_orm_pack.sqlmodules import *
from typing import Tuple, List

from httpx import AsyncClient

from database import SqlLiteQrm, get_session_decor
from helpful import sync_http_get


# sys.path.append(r"C:\Users\denis\PycharmProjects\sync_thread")
# from sync_mod_data import *


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

    async def main_scan_group(self):

        tasks = []
        time_sleep_thread = 0
        for x in range(self.count_thread):
            time_sleep_thread += 0.3
            tasks.append(
                SearchUserInGroup.scan_group(
                    time_sleep_thread,
                    self.count_offset_thread[x],
                    self.name_group,
                    self.token,
                    self.version_api))

        await gather(*tasks)

    @get_session_decor
    async def search(self):

        sq.CreateTable("user", {
            'id': toTypeSql(int),
            'sex': toTypeSql(int),
            'bdata': toTypeSql(int),
            'city': toTypeSql(int),
            'cwpm': toTypeSql(int),
            'followers': toTypeSql(int),
            'relation': toTypeSql(int),
            'last_seen': toTypeSql(int)
        })
        sq.CreateTable('sorted_users', {'id_user': toTypeSql(int)})
        run(self.main_scan_group())

    def show_search(self, limit_show: int = 10, width_column: int = 20):
        now = time()
        sq = SqlLiteQrm(f"group/{self.name_group}.db")

        sq.Search(Select('user', "*").Where("""sex == 1 AND 
        bdata BETWEEN 1999 AND 
        2001 AND city == 2 AND 
        cwpm == 1 AND 
        followers <= 800 AND 
        (relation == 0 OR relation == 6 OR relation == 1) AND 
        last_seen >={0}
        """.format(now - 604800)).Limit(limit_show), FlagPrint=width_column)

        sq.Search(Select('user', CountSql("id")).Where("""
                sex == 1 AND 
                bdata BETWEEN 1999 AND 
                2001 AND city == 2 AND 
                cwpm == 1 AND 
                followers <= 800 AND 
                (relation == 0 OR relation == 6 OR relation == 1) AND 
                last_seen >={0}
                """.format(now - 604800)), FlagPrint=width_column)

        sq.ExecuteTable('sorted_users', sqlRequest=Select('user', "id").Where("""
        sex == 1 AND 
        bdata BETWEEN 1999 AND 
        2001 AND city == 2 AND 
        cwpm == 1 AND 
        followers <= 800 AND 
        (relation == 0 OR relation == 6 OR relation == 1) AND 
        last_seen >={0}
        """.format(now - 604800)).Request)

        sq.GetTable('sorted_users', LIMIT=(10, 0), FlagPrint=12)

    def show_table(self, limit_show: int = 10, width_column: int = 20):
        sq = SqlLiteQrm(f"group/{self.name_group}.db")
        sq.Search(Select('user', "*").Limit(limit_show), FlagPrint=width_column)
        sq.Search(Select('user', CountSql("id")).Limit(limit_show), FlagPrint=width_column)

    @staticmethod
    async def scan_group(time_sleep_thread: float,
                         padding: Tuple[int, int],
                         group_name: str,
                         token_vk: str,
                         v: str):
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

        def saveDb(arr_user: List):
            # Сохраняем данные в БД
            if len(arr_user) >= counts:
                print(f"[INFO]\t{time_sleep_thread}\t- Записывает данные в БД -")
                thread_sq.ExecuteManyTable('user', arr_user)
                return True
            return False

        thread_sq = SqlLiteQrm(f"group/{group_name}.db")
        counts = 1000
        offset = padding[0]

        while offset <= padding[1]:
            async with AsyncClient() as session:
                responseGet = await session.get('https://api.vk.com/method/groups.getMembers', params={
                    "access_token": token_vk,
                    'v': v,
                    "group_id": group_name,
                    'count': counts,
                    'offset': offset,
                    'fields': 'sex,city,bdate,followers_count,relation,can_write_private_message,last_seen'
                })
                responseJson = responseGet.json()

            print(padding[1] - offset)
            offset += counts
            try:
                for i in responseJson['response']['items']:
                    try:
                        SearchUserInGroup.all_id.append((i['id'],  # id пользователя
                                                         i['sex'],  # Пол
                                                         int(i['bdate'].split('.')[2]),  # Дата рождения
                                                         i['city']['id'],  # Город
                                                         i['can_write_private_message'],  # Возможность писать сообщения
                                                         i['followers_count'],  # Количество подпищеков
                                                         i['relation'],  # Семенное положение
                                                         i["last_seen"]["time"]  # Дата последнего посещения ВК
                                                         ))

                    except (IndexError, KeyError):
                        SearchUserInGroup.user_false += 1  # Количество пользователи которые не имели таких полей
            except KeyError:
                if responseJson["error"]["error_code"] == 6:
                    print("Слишком много запросов в секунду, данные не полученные с сервера, увеличите задержку")
                else:
                    print(responseJson["error"]["error_code"])
            if saveDb(SearchUserInGroup.all_id):
                SearchUserInGroup.all_id.clear()

            await sleep(time_sleep_thread)
