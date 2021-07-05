import os
import sys
import threading
import time
from typing import Dict, Tuple

import requests

sys.path.append(r"C:\Users\denis\PycharmProjects\pall")
from sqlliteorm.sqlmodules import *
from sqlliteorm.sqllite_orm import *
from sync_thread_pack.sync_mod_data import *
SyncModDataSkippIterQueue.DEBUG_INFO = True

user_false = 0


def get_my_password(path_config: str) -> Dict[str, str]:
    try:
        with open(path_config, 'r') as fl:
            fl = fl.read().split('\n')
            if len(fl) == 3:

                return {"token": fl[0], "name": fl[1], "password": fl[2]}
            else:
                raise IOError("Неправильный формат ввода пароля")

    except FileNotFoundError:
        raise IOError("Отсутствует фал config.txt")


class SearchUserInGroup:

    def __init__(self, token_vk: str, group_name: str,
                 versionApi: str,
                 count_thread: int = 1,
                 limit_get_user_group: int = 0,
                 ):
        """
        :param token_vk: Токен VK
        :param group_name: ID группы
        :param count_thread: Кооличесвто потоков проыессора
        :param versionApi: Версия VK API
        :param limit_get_user_group: Колличесво участников по умолчанию все
        """
        self.token = token_vk
        self.name_group = group_name if group_name.find("https://vk.com/") == -1 else group_name[15::]
        self.count_thread = count_thread
        self.v = versionApi
        self.count_user = self.get_cont_user_group() if not limit_get_user_group else limit_get_user_group

        os.makedirs('group') if not os.path.exists('group') else None

        # Отступы по участникам для потоков
        self.count_offset_thread = SyncModData.offset_thread(self.count_user, self.count_thread)

    def get_cont_user_group(self) -> int:
        response = requests.get('https://api.vk.com/method/groups.getMembers', params={
            "access_token": self.token,
            'v': self.v,
            "group_id": self.name_group,
            'count': 1,
            'offset': 1,
        })
        res: dict = response.json()
        if res.get('error'):
            if res['error']["error_code"] == 125:
                raise ValueError("Неправильный id группы")
            if res['error']["error_code"] == 5:
                raise ValueError("У вас Неверный Токен ID")

            raise ValueError(res)

        return res['response']['count']

    def search(self):

        time_sleep_thread = 0
        thread_list = []

        sq = SqlLiteQrm(f"group/{self.name_group}.db")
        sq.DeleteTable(["user", "sorted_users"])
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

        for x in range(self.count_thread):
            time_sleep_thread += 0.3
            t = threading.Thread(target=SearchUserInGroup.scan_group, args=(
                SyncModDataSkippIterQueue(f"Th_{x}"),
                time_sleep_thread,
                self.count_offset_thread[x],
                self.name_group,
                self.token,
                self.v))
            thread_list.append(t)
            t.start()
        for y in thread_list:
            y.join()

    def show_search(self, limit_show: int = 10, width_column: int = 20):
        now = time.time()
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
    def scan_group(LockTrigger: SyncModDataSkippIterQueue,
                   time_sleep_thread: float,
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

        global user_false
        _LockWriteSql = threading.Lock()

        thread_sq = SqlLiteQrm(f"group/{group_name}.db")
        counts = 1000
        offset = padding[0]
        all_id: list = []
        while offset <= padding[1]:
            response = requests.get('https://api.vk.com/method/groups.getMembers', params={
                "access_token": token_vk,
                'v': v,
                "group_id": group_name,
                'count': counts,
                'offset': offset,
                'fields': 'sex,city,bdate,followers_count,relation,can_write_private_message,last_seen'
            })
            offset += counts
            print(padding[1] - offset)
            try:
                for i in response.json()['response']['items']:
                    try:
                        all_id.append((i['id'],  # id пользователя
                                       i['sex'],  # Пол
                                       int(i['bdate'].split('.')[2]),  # Дата рождения
                                       i['city']['id'],  # Город
                                       i['can_write_private_message'],  # Возможность писать сообщения
                                       i['followers_count'],  # Колличество подпищеков
                                       i['relation'],  # Семеной положение
                                       i["last_seen"]["time"]  # Дата последнего посещения ВК
                                       ))
                    except (IndexError, KeyError):
                        user_false += 1  # Колличесво пользователи которые не имели таких полей
            except KeyError:
                if response.json()["error"]["error_code"] == 6:
                    print("Слишком много запросов в секнду, данные не полученны с сервера")
                else:
                    print(response.json())

            # Сохраняем данные в БД
            if len(all_id) >= counts and LockTrigger.is_lock():
                """
                Синхранизация записи потоков. Если запись занята потоки будут продолжать 
                получать даные из интерент и хранить их в ОЗУ
                """
                print(f"[INFO]\t\t- Записывает данные в БД -")

                thread_sq.ExecuteManyTable('user', all_id)
                all_id.clear()

                LockTrigger(lock=False)

            # Псевдо Защита от привышения лимита получения пользователе Вк
            time.sleep(time_sleep_thread)


name_group = "https://vk.com/mudakoff"

if __name__ == "__main__":
    token = get_my_password(r"C:\Users\denis\PycharmProjects\pythonProject11\config.txt")["token"]
    my_class = SearchUserInGroup(
        token_vk=token,
        group_name=name_group,
        count_thread=3,
        versionApi="5.131")

    # 732613 * 3
    # if True:
    #     print('===========================')
    #     print(my_class.get_cont_user_group())
    #     print('===========================')
    #     my_class.search()
    #     print('===========================')
    #     print(my_class.get_cont_user_group())
    #     print(user_false)

    my_class.show_table(limit_show=3, width_column=10)
    my_class.show_search(limit_show=3, width_column=10)
