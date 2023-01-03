import asyncio
from pathlib import Path

from helpful import get_my_password,show_necessary_users
from vk_collect import CollectUserFomGroup
from mg_sql.sql_async import SqlUrlConnect
from mg_sql.sql_async.base import SQL
from model_db import UsersVk,GroupsVk,LikeUser
from json import dumps

p_binary = Path(__file__).parent.parent / 'binary'

SQL(SqlUrlConnect.sqllite(path_db=(p_binary / 'sql_db.sqlite').resolve()))

def collect_user_from_group_vk(name_group: str):
    """
    Собрать в БД пользователи указанной группы  ВК
    """
    token = get_my_password(r"config.json")["token"]
    my_class = CollectUserFomGroup(
        token_vk=token,
        group_name=name_group,
        versionApi="5.131",
        # limit_get_user_group=20_000
    )
    print(my_class.count_user)
    asyncio.run(my_class.run())
    print('Не подходящие записи: ',CollectUserFomGroup.user_false)

def view():
    # Показать и записать в файл, подходящих пользовательниц
    res=asyncio.run(show_necessary_users())
    print(res)
    (p_binary / 'necessary_users.json').write_text(dumps(res))

def create_table():  
    # Создать Таблицы  
    asyncio.run(SQL.create_models(
        [GroupsVk,UsersVk,LikeUser]
    ))

if __name__ == "__main__":
    # search(name_group= "https://vk.com/open_sourcecode"
        # "https://vk.com/kinomania"
    # )
    # create_table()
    view()
    