import datetime
import time

import requests
import threading
import json
import os

from See import data_private

all_id = []
user_false = 0


def vK_scan(time_sleep_therad: float, padding, name_group, token, v):
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

    global all_id, user_false
    counts = 1000
    offset = padding[0]
    while offset <= padding[1]:
        response = requests.get('https://api.vk.com/method/groups.getMembers', params={
            "access_token": token,
            'v': v,
            "group_id": name_group,
            'count': counts,
            'offset': offset,
            'fields': 'sex, city, bdate,followers_count,relation,can_write_private_message,last_seen'
        })
        offset += counts
        print(
            (((padding[1] - offset) - (padding[1] - padding[0])) * -1) // counts)

        try:
            for i in response.json()['response']['items']:
                try:
                    all_id.append((i['id'], i['sex'], int(i['bdate'].split('.')[2]), i['city']['id'],
                                   i['can_write_private_message'], i['followers_count'], i['relation'],
                                   i["last_seen"]["time"]))
                except KeyError:
                    user_false += 1
                except IndexError:
                    user_false += 1

        except KeyError:
            if response.json()["error"]["error_code"] == 5:
                print("Неверный Токен")
                return
            print(response.json())

        time.sleep(time_sleep_therad)


class Search_Friends():

    def __init__(self, token: str, name_group: str, count_user: int, count_therad: int, versionApi: str):
        self.name_group = name_group
        self.countThered = count_therad
        self.Error_list = []  # str()
        self.token = token
        self.v = versionApi

        if count_user == 0:
            self.count_user = self.get_cont_user_group()
        else:
            self.count_user = count_user

        self.count_offset_thered = self.sorted_numbers(self.count_user, self.countThered)
        self.all_id = []
        self.thered_list = []

        self.open_read_file()
        self.countAllVerifiedUsers = 0

    def sorted_numbers(self, number_all, countThered):
        b = number_all // (countThered)  # 10
        v = []
        d = []
        for u in range(countThered):
            v.append(number_all)
            number_all = number_all - b
            if u > 0:
                f = v[u], v[u - 1]
                d.append(f)
                if u + 1 == countThered:
                    v.append(number_all)
                    f = v[u + 1], v[u]
                    d.append(f)
        return d

    def open_read_file(self):
        try:
            os.mkdir(self.name_group)
        except OSError as error:
            # Файл существут
            self.Error_list.append(error)

    def search(self):
        # for x in range(self.countThered):
        #     vK_scan(self.count_offset_thered[x], self.name_group, self.token, self.v)

        time = 0
        for x in range(self.countThered):
            time += 0.3
            t = threading.Thread(target=vK_scan,
                                 args=(time, self.count_offset_thered[x], self.name_group, self.token, self.v))

            self.thered_list.append(t)
            t.start()
        for y in self.thered_list:
            y.join()

    def cleaned_id(self):
        now = time.time()
        n = []
        for x in self.all_id:
            if x[1] == 1:
                if x[2] >= 1999 and x[2] <= 2001:
                    if x[3] == 2:
                        if x[4] == 1:
                            if x[5] <= 800:
                                if x[6] == 0 or x[6] == 6 or x[6] == 1:
                                    # Проветрить тщательно время последнего посещение сайта
                                    if x[7] >= (now - 604800):  # (now - 604800) = 7 дней
                                        n.append(x)
                                        self.countAllVerifiedUsers += 1

        with open('{}\\userId.json'.format(self.name_group), 'w') as file_json:
            json.dump(n, file_json)

    def get_cont_user_group(self) -> int:
        response = requests.get('https://api.vk.com/method/groups.getMembers', params={
            "access_token": self.token,
            'v': self.v,
            "group_id": self.name_group,
            'count': 1,
            'offset': 1,
        })
        return response.json()['response']['count']


if __name__ == "__main__":
    start_time = time.time()

    name_group = "tproger"

    dt = data_private()
    csSF = Search_Friends(token=dt["token"],
                          name_group=name_group,
                          count_user=0,
                          count_therad=3,
                          versionApi="5.131")
    all_id = csSF.all_id
    csSF.search()
    csSF.cleaned_id()

    print('++++++++++++++++++++++++++')
    print("Время поиска: {0}\nНайденно: {1}\nПрошедшие Проверку: {2}\nОшибки Поиска: {3}\nОшибки Сисетмы: {4}".format(
        time.time() - start_time,
        csSF.count_user - user_false,
        csSF.countAllVerifiedUsers,
        user_false,
        csSF.Error_list))
