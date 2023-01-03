import asyncio
from pathlib import Path
from typing import Literal

from helpful import get_my_password, show_necessary_users, show_like_users
from vk_collect import CollectUserFomGroup
from mg_sql.sql_async import SqlUrlConnect
from mg_sql.sql_async.base import SQL
from model_db import UsersVk, GroupsVk, LikeUser
from json import dumps
from viewer_selenium import ViewSelenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


#############################
# Глобальные переменные
name_group = "https://vk.com/open_sourcecode"
passwords = get_my_password(r"config.json")
token = passwords['token']
# Путь к папке с бинарными данными
p_binary = Path(__file__).parent.parent / 'binary'
##############################
# Создаем подключение с БД
SQL(SqlUrlConnect.sqllite(path_db=(p_binary / 'sql_db.sqlite').resolve()))


def collect_user_from_group_vk(name_group: str, token: str):
    """
    Собрать в БД пользователи указанной группы  ВК
    """
    my_class = CollectUserFomGroup(
        token_vk=token,
        group_name=name_group,
        versionApi="5.131",
        # limit_get_user_group=20_000
    )
    print(my_class.count_user)
    asyncio.run(my_class.run())
    print('Не подходящие записи: ', CollectUserFomGroup.user_false)


def view(type_view: Literal['all', 'like']):
    """
    Показать и записать в файл, подходящих пользовательниц
    
    type_view: all-Все пользователи. like-только отлайканные
    """
    ##
    # Запустить силениум
    ##

    match type_view:
        case 'like':
            list_all_user_vk = asyncio.run(show_like_users())
        case 'all':
            list_all_user_vk = asyncio.run(show_necessary_users())
        case _:
            raise Exception('Неверный тип показа')

    options = Options()
    ViewSelenium(
        user_name=passwords["name"],
        password=passwords["password"],
        list_all_user_vk=list_all_user_vk,
        type_view=type_view,
        path_to_driver=p_binary/'geckodriver.exe',
        path_to_browser=r'C:\Program Files\Mozilla Firefox\firefox.exe',
        options=options
    )


def create_table():
    """
    Создать Таблицы  
    """
    asyncio.run(SQL.create_models(
        [GroupsVk, UsersVk, LikeUser]
    ))


if __name__ == "__main__":
    # search(name_group= "https://vk.com/kinomania",token)
    # create_table()
    view('all')
