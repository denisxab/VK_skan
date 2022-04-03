import asyncio

from mg_file import EnvFile

EnvFile('__env.env').readAndSetEnv()

from helpful import get_my_password
from vk_scan import SearchUserInGroup


def search(name_group: str):
    token = get_my_password(r"config.json")["token"]
    my_class = SearchUserInGroup(
        token_vk=token,
        group_name=name_group,
        versionApi="5.131",
        limit_get_user_group=20_000
    )

    print(my_class.count_user)
    asyncio.run(my_class.search())
    # print(SearchUserInGroup.user_false)
    # my_class.show_table(limit_show=3, width_column=10)
    # my_class.show_search(limit_show=3, width_column=10)


def view():
    ...
    asyncio.run(SearchUserInGroup.show_search())


if __name__ == "__main__":
    search(name_group="https://vk.com/kinomania")
    # view()
