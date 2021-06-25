import sqlite3
from os import remove
from os.path import exists, abspath
from sqlite3 import Binary
from typing import List, Tuple, Dict, Union

from file import TxtFile


class sqn:
    PK: str = "PRIMARY KEY"  # Должны содержать ункальные значения
    NN: str = "NOT NULL"  # Всегда должно быть заполенно
    NND = lambda default=None: \
        "NOT NULL DEFAULT {0}".format(default)  # Все столбцы будут по умолчанию заполнены указанными значениями
    DEFAULT = lambda default=None: "DEFAULT {0}".format(default)
    IDAUTO: str = "PRIMARY KEY AUTOINCREMENT"  # Авто заполение строки. подходит для id

    # Агрегирущие функции
    count = lambda arg: "count(DISTINCT {0})".format(arg[1::]) if arg[0] == "-" else "count({0})".format(arg)
    sum = lambda arg: "sum(DISTINCT {0})".format(arg[1::]) if arg[0] == "-" else "sum({0})".format(arg)
    avg = lambda arg: "avg(DISTINCT {0})".format(arg[1::]) if arg[0] == "-" else "avg({0})".format(arg)
    min = lambda arg: "min(DISTINCT {0})".format(arg[1::]) if arg[0] == "-" else "min({0})".format(arg)
    max = lambda arg: "max(DISTINCT {0})".format(arg[1::]) if arg[0] == "-" else "max({0})".format(arg)

    #:Union[str, Tuple] выбор столбцов
    select = lambda *sel: ', '.join(sel)

    #:Union[str, Tuple] сиять таблицы
    InnerJoin = lambda name_table, ON: \
        "INNER JOIN {0} ON {1}".format(name_table, ', '.join(ON)) \
            if type(ON) == tuple \
            else "INNER JOIN {0} ON {1}".format(name_table, ON)

    #:Union[str, Tuple] сиять таблицы даже если они не равны
    LeftJoin = lambda name_table, ON: \
        "LEFT JOIN {0} ON {1}".format(name_table, ', '.join(ON))

    #:Union[str, Tuple] групировать
    group_by = lambda *group: \
        " GROUP BY {0}".format(', '.join(group))

    #:str сортировать
    order_by = lambda order: \
        " ORDER BY {0} DESC".format(order[1::]) \
            if order[0] == '-' \
            else ' ORDER BY {0} ASC'.format(order)

    # int лимит вывода
    limit = lambda lim, offset=0: \
        " LIMIT {0} OFFSET {1}".format(lim, offset)


def toDictSql(sql_request: str) -> Dict[str, tuple]:
    # Зависит от SqlName
    """
    # Доделать оброботку дополнительных пармаетров

    :param sql_request: Sql запрос
    :return: словарь который поддерживает класс SqlLite
    """
    res_dict = {}
    # Конвертировать SQL запросв в header_db
    for d in sql_request[1:-1:].split(","):

        if d.find("TEXT") != -1:
            v = str
        elif d.find("INTEGER") != -1:
            v = int
        elif d.find("REAL") != -1:
            v = float
        elif d.find("BLOB") != -1:
            v = bytes
        elif d.find("NULL") != -1:
            v = None
        else:
            raise TypeError(
                "Указан не верный тип данных выбирете TEXT;INTEGER;REAL;BLOB;NULL\n{0}".format(d))

        two = ""
        # Сначало длинные слова потом короткие
        if d.find("PRIMARY KEY AUTOINCREMENT") != -1:
            two = "PRIMARY KEY AUTOINCREMENT"
        elif d.find("PRIMARY KEY") != -1:
            two = "PRIMARY KEY"
        #
        elif d.find("NOT NULL DEFAULT") != -1:
            two = "NOT NULL DEFAULT {0}".format(d.split(" ")[:-1:])
        elif d.find("DEFAULT") != -1:
            two = "DEFAULT"
        elif d.find("NOT NULL") != -1:
            two = "NOT NULL"

        res_dict[d.lstrip().split(" ")[0]] = (v, two)

    return res_dict


def toSqlRequest(data: Dict[str, Union[tuple, str]]) -> str:
    """
    :param data: словарь по стандартам класса SqlLite
    :return: SQl запрос
    """
    count_primary_key = False
    # Конвертация словаря в SQL запрос
    res = "("
    for k, v in data.items():
        res += str(k)

        if type(v) == tuple and len(v) == 2:  # Комбенированная запись с параметрами столбца

            if v[1] == sqn.PK or v[1] == sqn.IDAUTO:  # Проверка уникальности Primary Key в таблицы
                if not count_primary_key:
                    count_primary_key = True
                else:
                    raise LookupError("Запрос имеет больше одного primary key")

            tmp = " {0}".format(v[1])
            values = v[0]
        else:  # Обыная запись столбца
            tmp = ''
            values = v

        if values == str:
            res += " TEXT"
        elif values == int:
            res += " INTEGER"
        elif values == float:
            res += " REAL"
        elif values == bytes:
            res += " BLOB"
        elif values is None:
            res += " NULL"
        else:
            raise TypeError(
                "Указан не верный тип данных выбирете str;int;float;None;bytes\n{0}:{1}".format(k, v))

        res += "{0}{1}".format(tmp, ", ")

    res = res[:-2:]
    res += ")"
    return res


class SqlLiteQrm:
    """
    - Запись данных в БД
    - Чтение данных Из БД
    """

    def __init__(self, name_dbf: str) -> None:  # +
        self.connection = None
        # Проверка того что разшерение db
        tmp = name_dbf.split(".")
        if len(tmp) != 2 or tmp[1] != "db":
            raise NameError("Файл должен иметь разшерение .db")

        self.name_db = name_dbf
        self.header_table: Dict[
            str, Dict[str, tuple]] = self.__update_header_table()  # Тут храниться типы столбцов таблциы

        # self.connection = sqlite3.connect(self.name_db)
        # self.cursor = self.connection.cursor()

    def __del__(self):  # +
        pass

    def ListTables(self) -> List[str]:  # +
        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [x[0] for x in cursor.fetchall() if x[0] != 'sqlite_sequence']

    def __update_header_table(self) -> Dict[str, Dict[str, tuple]]:  # +
        # Получение схемы всех таблиц в бд
        res: Dict[str, Dict[str, tuple]] = {}

        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            for x in self.ListTables():
                meta = cursor.execute("PRAGMA table_info({0})".format(x))

                """
                (номер имни, имя, тип данных,NOT NULL, значение по умолчанию, PRIMARY KEY )
                """
                res[x] = {}
                for r in meta:

                    type_name = r[2]

                    res_type = None
                    if type_name == "TEXT":
                        res_type = str
                    elif type_name == "INTEGER":
                        res_type = int
                    elif type_name == "REAL":
                        res_type = float
                    elif type_name == "BLOB":
                        res_type = bytes

                    res_nn: str = ""
                    if r[3] == 1:
                        res_nn = "NOT NULL"

                    if r[4] != None:
                        res_nn += "DEFAULT {0}".format(r[4])

                    if r[5] == 1:
                        res_nn = "PRIMARY KEY"

                    res[x].update({r[1]: (res_type, res_nn)})

        return res

    def DeleteDb(self):  # +
        if exists(self.name_db):
            remove(abspath(self.name_db))

    def DeleteTable(self, name_tables: Union[str, List[str]]):  # +

        # Удалить несоклько таблиц
        if type(name_tables) == list:
            for item in name_tables:
                if self.header_table.get(item):
                    self.header_table.pop(item)
                with sqlite3.connect(self.name_db) as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "DROP TABLE IF EXISTS {0};".format(item))  # Удалить таблицу если она существует

        else:
            if self.header_table.get(name_tables):
                self.header_table.pop(name_tables)
            with sqlite3.connect(self.name_db) as connection:
                cursor = connection.cursor()
                cursor.execute("DROP TABLE IF EXISTS {0};".format(name_tables))  # Удалить таблицу если она существует

    def CreateTable(self, name_table: str, data: Union[str, Dict]):  # +

        # Конвертация типов в str
        res: str = ""
        if type(data) == str:
            res = data
            self.header_table[name_table] = toDictSql(res)

        elif type(data) == dict:
            res = toSqlRequest(data)

            for k, v in data.items():
                data[k] = (v, "") if type(v) != tuple else v

            self.header_table[name_table] = data

        # Создание таблицы
        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS {0} {1}".format(name_table, res))

    def ExecuteTable(self, name_table: str,
                     data: Union[str, List[Union[str, bytes, int, float]],
                                 Tuple,
                                 Dict[str, Union[str, bytes, int, float]]],
                     sqlRequest: str = "",
                     CheckBLOB: bool = False
                     ):  # +
        """
        :param name_table:
        :param data:
        :param sqlRequest:
        :param CheckBLOB: проверка стурктуры на анличие бинарных бинырных данных и перевод их  в sqlite3.Binary()
        :return:
        """
        request: str = "INSERT INTO {0}".format(name_table)

        if sqlRequest:  # для вложенных запрсов
            request += " {0}".format(sqlRequest)
            data = None

        else:
            if type(data) == str:  # Для SQL команд
                if data.find("bytes") != -1:
                    raise TypeError(
                        "Нельзя отпраять BLOB в формате строки. Воспользуйтесь добавление данных через list")
                request += " {0} VALUES {1}".format(tuple(self.header_table[name_table].keys()), data)
                data = None

            else:  # Для структур данных
                res: str = ', '.join('?' * len(data))

                # Конвертация типа в dict в SQL запрос
                if type(data) == dict:
                    if tuple(data.keys() - self.header_table[name_table].keys()):
                        raise IndexError("Именя переданного столбца неуществует")

                    request += " {0} VALUES ({1})".format(tuple(data.keys()), res)

                    if CheckBLOB:
                        data = list(data.values())
                        for index1, tup in enumerate(data):
                            if type(tup) == bytes:
                                data[index1] = Binary(tup)
                        data = tuple(data)
                    else:
                        data = tuple(data.values())

                # Конвертация типов list, tuple в SQL запрос
                elif type(data) == tuple or type(data) == list:
                    if len(data) != len(self.header_table[name_table]):
                        raise IndexError("Разное колличество столбцов таблицы и входных данных")

                    request += " {0} VALUES ({1})".format(tuple(self.header_table[name_table].keys()), res)

            with sqlite3.connect(self.name_db) as connection:
                cursor = connection.cursor()
                cursor.execute(request, data) if data else cursor.execute(request)

    def __CheackBlob(self, data: List[Union[List[Union[str, bytes, Binary, int, float]], Tuple]]) -> \
            List[Union[List[Union[str, bytes, Binary, int, float]], Tuple]]:

        if type(data[0]) == tuple:
            raise TypeError("Нельзя использовать параметер CheckBLOB на структуре данных tuple. используйте list")
        for index1, it in enumerate(data):
            for index2, tup in enumerate(it):
                if type(tup) == bytes:
                    data[index1][index2] = Binary(tup)
        return data

    def ExecuteManyTable(self, name_table: str,
                         data: List[Union[List[Union[str, bytes, Binary, int, float]], Tuple]],
                         countNull: int = 0,
                         CheckBLOB: bool = False
                         ):  # +
        """
        :param name_table:
        :param data:
        :param countNull: Ставит NULL в начале указанное колличество раз
        :param CheckBLOB: проверка стурктуры на анличие бинарных бинырных данных и перевод их  в sqlite3.Binary()
        :return:
        """
        if type(data) != list:
            raise TypeError("Должен быть тип List")

        res: str = ""

        # Для пропуска значений например PRIMARY KEY AUTOINCREMENT
        if countNull:
            res = 'NULL, ' * countNull
        res += ', '.join('?' * (len(self.header_table[name_table]) - countNull))

        request: str = "INSERT INTO {nt} {name_arg} VALUES ({values})".format(nt=name_table,
                                                                              name_arg=tuple(
                                                                                  self.header_table[name_table].keys()),
                                                                              values=res)

        if CheckBLOB:
            data = self.__CheackBlob(data)

        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.executemany(request, data)

    def ExecuteManyTableDict(self, name_table: str, data: List[Dict]):  # +

        for dict_x in data:
            res: str = ', '.join('?' * len(dict_x))
            ae = "INSERT INTO {nt} {name_arg} VALUES ({values})".format(nt=name_table,
                                                                        name_arg=tuple(dict_x.keys()),
                                                                        values=res)
            with sqlite3.connect(self.name_db) as connection:
                cursor = connection.cursor()
                cursor.execute(ae, tuple(dict_x.values()))

    def HeadTable(self, name_table, width_table) -> str:
        res = self.__print_table(name_table, ", ".join(self.header_table[name_table].keys()),
                                 [[str(x) for x in self.header_table[name_table].values()]], width_table)

        return res

    def GetTable(self, name_table: str,
                 sqlLIMIT: sqn.limit = "",
                 FlagPrint: int = 0
                 ) -> list:  # +
        """
        Конвертация bytes в обьекта SQl BLOB и обратно
        a = Binary(b"101101")
        print(a.tobytes())
        """

        request: str = 'SELECT * FROM {0}'.format(name_table)

        if sqlLIMIT:
            request += sqlLIMIT

        # Получить данные из таблицы
        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute(request)
            res = cursor.fetchall()
            if FlagPrint:
                print(self.__print_table(name_table, ", ".join(self.header_table[name_table].keys()), res, FlagPrint))
            return res

    def GetColumn(self, name_table: str, name_columns: str) -> list:  # +
        # Получить данные из столбца
        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT {0} FROM {1}'.format(name_columns, name_table))
            return [x[0] for x in cursor.fetchall()]

    def SearchColumn(self, name_table: str,
                     sqlSelect: sqn.select,
                     sqlJOIN: sqn.InnerJoin = "",  # [List[str],List[Union[str,List]]] = "",
                     sqlWHERE: str = "",
                     sqlLIKE: str = "",
                     sqlGROUPBY: sqn.group_by = "",
                     sqlORDER_BY: sqn.order_by = "",
                     sqlLIMIT: sqn.limit = "",
                     FlagPrint: int = 0,
                     FlagReturnSqlRequest: bool = False
                     ) -> Union[List[tuple], str]:  # +
        """



        :param name_table: Название таблицы
        :param sqlSelect: sqn.select :Union[str, Tuple]
        :param sqlJOIN: sqn.InnerJoin||LeftJoin :Union[str, Tuple]
        :param sqlWHERE: условие
        :param sqlLIKE:
        :param sqlGROUPBY:  sqn.group_by :Union[str, Tuple]
        :param sqlORDER_BY: sqn.order_by :str
        :param sqlLIMIT:sqn.limit :int
        :param FlagPrint: Отобразить в консоли
        :param FlagReturnSqlRequest: Вернет сформированный SQL запрос
        :return:
        """
        """
        Получение данных из курсора
        cursor.fetchone() - получить только первую запись
        cursor.fetchmany() - получить только до указаонного колличества
        cursor.fetchall() - получить все записи
        for x in cursor - переберать по одному элементу(данные в виде итератора)      
        """

        request: str = 'SELECT {0} FROM {1}'.format(sqlSelect, name_table)

        if sqlJOIN:
            request += " {0}".format(sqlJOIN)

        if sqlWHERE:
            request += " WHERE {0}".format(sqlWHERE)

        if sqlLIKE:
            # % любое продолжение строк
            # _ любой один симвл
            request += " LIKE '{0}'".format(sqlLIKE)

        if sqlGROUPBY:
            request += sqlGROUPBY

        if sqlORDER_BY:
            request += sqlORDER_BY

        if sqlLIMIT:
            request += sqlLIMIT

        if FlagReturnSqlRequest:
            return request

        else:
            with sqlite3.connect(self.name_db) as connection:
                cursor = connection.cursor()
                cursor.execute(request)
                res = cursor.fetchall()

            if FlagPrint:
                if sqlSelect == "*":
                    sqlSelect = ", ".join(self.header_table[name_table].keys())
                print(self.__print_table(name_table, sqlSelect, res, FlagPrint))

            return res

    def __print_table(self, name_table: str,
                      head: str,
                      data_list: List[Union[list, tuple]],
                      width_table: int = 5,
                      ) -> str:
        res: str = ""
        head = head.split(", ")
        for i, p in enumerate(head):
            head[i] = p.center(width_table)
        head = '¦'.join(head)
        lain = "+{0}+".format("-" * len(head))

        res += lain + "\n"
        res += "|{}|\n".format(name_table.center(len(lain) - 2))
        res += lain + "\n"
        res += "|{0}|\n".format(head)

        for p in data_list:
            res += lain + "\n"
            p = list(p)
            for i, d in enumerate(p):
                p[i] = str(d).center(width_table)

            res += "|{}|\n".format('¦'.join(p))
        res += lain + "\n"

        return res

    def UpdateColumne(self, name_table: str,
                      name_column: Union[str, List[str]],
                      new_data: Union[str, bytes, int, float, List[Union[str, bytes, int, float]]],
                      sqlWHERE: str = "",
                      sqlLIKE: str = ""):
        """
        Обновлени данных в стобцах
        :param name_table: Название таблицы
        :param name_column: Название столбца котроый будет выбора
        :param new_data: Новое значение у столбцов
        :param sqlWHERE: Условие SQL полсе WHERE
        :param sqlLIKE: Шаблон SQL посе LIKE
        """

        request: str = "UPDATE {0} SET ".format(name_table)
        if type(name_column) == list and type(new_data) == list:  # Нескольк столбцов на измнение
            if len(name_column) != len(new_data):
                raise IndexError("name_column != new_data")

            for n, d in zip(name_column, new_data):
                if type(n) == str:
                    request += "{0} = '{1}', ".format(n, d)
                else:
                    request += "{0} = {1}, ".format(n, d)
            request = request[:-2:]
        else:  # один столбцов на измнение
            request += "{0} = {1}".format(name_column, new_data)

        if sqlWHERE:
            request += " WHERE {0}".format(sqlWHERE)
        if sqlLIKE:
            # % любое продолжение строк
            # _ любой один симвл
            request += " LIKE '{0}'".format(sqlLIKE)

        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute(request)

    def DeleteLineTable(self,
                        name_table: str,
                        sqlWHERE: str = "",
                        sqlLIKE: str = ""):
        """
        :param name_table: Название таблицы
        :param sqlWHERE: Условие SQL полсе WHERE
        """
        request: str = "DELETE FROM {0}".format(name_table)

        if sqlWHERE:
            request += " WHERE {0}".format(sqlWHERE)

        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            cursor.execute(request)

    def SaveDbToFile(self, name_save_db):
        tm = TxtFile(name_save_db)
        tm.deleteFile()
        with sqlite3.connect(self.name_db) as connection:
            for sql in connection.iterdump():
                tm.appendFile(sql)

    def ReadFileToDb(self, name_read_db):
        tm = TxtFile(name_read_db)
        with sqlite3.connect(self.name_db) as connection:
            cursor = connection.cursor()
            # Это все для того чтобы пропустить эти строки которые возникают непонятно почему
            # DELETE FROM "sqlite_sequence";INSERT INTO "sqlite_sequence" VALUES('stocks',3);
            cursor.execute("BEGIN TRANSACTION;")
            tmp = False
            for text in tm.readFile().split(";"):
                if tmp:
                    cursor.execute(text)
                else:
                    if text.find("CREATE") != -1:
                        tmp = True
                        cursor.execute(text)


if __name__ == '__main__':
    name_db = 'example.db'
    name_table = "cadrs"
    sq = SqlLiteQrm(name_db)
    # sq.ReadFileToDb("testsave.txt")

    sq.CreateTable(name_table, {
        'car_id': (int, sqn.IDAUTO),
        "model": str,
        "price": bytes
    })
    cars = [
        ["Audi", b'432'],
        ["Maer", b'424'],
        ["Skoda", b"122"]
    ]
    sq.ExecuteManyTable(name_table, cars, countNull=1, CheckBLOB=True)

    with sqlite3.connect('example.db') as connection:
        for sql in connection.iterdump():
            print(sql)

    sq.GetTable(name_table, FlagPrint=10)
    # sq.SaveDbToFile("testsave.txt")
    # sq.ReadFileToDb("testsave.txt")
