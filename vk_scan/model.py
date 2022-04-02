from asyncio import run
from os import environ
from pathlib import Path

from mg_file import EnvFile
from sqlalchemy import Integer, Column, ForeignKey, String

EnvFile(str(Path('../__env.env').resolve())).readAndSetEnv()

from database import SQL, UrlConnect

SQL(UrlConnect.sqllite(environ["DATA_BASE_NAME"]))


class UsersVk(SQL.Base):
    __tablename__ = 'users_vk'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, unique=True)
    groups_id = Column(Integer, ForeignKey("group_vk.id", onupdate="CASCADE", ondelete="CASCADE"))
    sex = Column(Integer, )
    bdata = Column(Integer, )
    city = Column(Integer, )
    cwpm = Column(Integer, )
    followers = Column(Integer, )
    relation = Column(Integer, )
    last_seen = Column(Integer, )

    # group = relationship("GroupsVk", backref="users_vk")

    def __repr__(self):
        return f"{self.id=},{self.groups_id=}"


class GroupsVk(SQL.Base):
    __tablename__ = 'group_vk'
    id = Column(Integer, primary_key=True)
    name_group = Column(String(255), nullable=False)

    def __repr__(self):
        return f"{self.id=},{self.name_group=}"


if __name__ == '__main__':
    run(SQL.create_tabel())
    # run(SQL.drop_tabel())
