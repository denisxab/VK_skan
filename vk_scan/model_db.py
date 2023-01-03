from mg_sql.sql_async.model_logic import RawSqlModel

class UsersVk(RawSqlModel):
    """Пользователи"""
    table_name = 'users_vk'

    @classmethod
    def create_table(cls) -> str:
        return """
CREATE TABLE users_vk (
	id INTEGER,
	user_id INTEGER,
	groups_id INTEGER,
	sex INTEGER,
	bdata INTEGER,
	city INTEGER,
	cwpm INTEGER,
	followers INTEGER,
	relation INTEGER,
    -- Время последнего посещения, на момент добавления записи
	last_seen INTEGER,
    -- Время добавления записи
    time_add integer,
	CONSTRAINT USERS_VK_PK PRIMARY KEY (id),
	CONSTRAINT FK_users_vk_group_vk FOREIGN KEY (groups_id) REFERENCES group_vk(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX ix_users_vk_user_id ON users_vk (user_id);
    """

class GroupsVk(RawSqlModel):
    """Группы"""
    table_name = 'group_vk'
    
    @classmethod
    def create_table(cls) -> str:
        return """
CREATE TABLE group_vk (
	id INTEGER,
	name_group VARCHAR(255),
	CONSTRAINT GROUP_VK_PK PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_group_vk_name_group ON group_vk (name_group);
    """

class LikeUser(RawSqlModel):
    """Лайки"""
    table_name = 'like_user'
    
    @classmethod
    def create_table(cls) -> str:
        return """
CREATE TABLE like_user (
	id INTEGER,
	user_id INTEGER,
	CONSTRAINT LIKE_USER_PK PRIMARY KEY (id),
	CONSTRAINT FK_like_user_users_vk FOREIGN KEY (user_id) REFERENCES users_vk(id) ON DELETE CASCADE ON UPDATE CASCADE
);
    """

