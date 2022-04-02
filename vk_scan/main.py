import asyncio
from pathlib import Path

from mg_file import EnvFile

EnvFile(str(Path('./__env.env').resolve())).readAndSetEnv()

from helpful import get_my_password
from vk_scan import SearchUserInGroup


def search(name_group: str):
    token = get_my_password(r"config.json")["token"]
    my_class = SearchUserInGroup(
        token_vk=token,
        group_name=name_group,
        versionApi="5.131"
    )

    # 732613 * 3
    if True:
        print('===========================')
        print(my_class.count_user)
        print('===========================')
        asyncio.run(my_class.search())
        print('===========================')
        print(my_class.count_user)
        print(SearchUserInGroup.user_false)
    #
    # my_class.show_table(limit_show=3, width_column=10)
    # my_class.show_search(limit_show=3, width_column=10)


def view():
    ...


if __name__ == "__main__":
    search(name_group="https://vk.com/kinomania")
