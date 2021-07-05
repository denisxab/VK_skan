""""
Создать класс для синхронной записи потоков
Если запись занята потоки пропускают итерацию
"""
import random
import time
from sys import getsizeof
from typing import List, Union


class SyncModData:

    # Создает потоки
    @staticmethod
    def CreateThread(count_thread: int, objectSync) -> \
            list:
        return [objectSync(f"Th_{item}") for item in range(1, count_thread)]

    def __init__(self, name: str = None):
        self.NameThread = str(name)  # Даем имя

    def __str__(self) -> str:
        return f"{self.NameThread}"

    def __call__(self, *, lock: bool):
        raise NotImplementedError()

    # для threading.Thread(target=testTherad, args=(th))
    def __iter__(self):
        return self

    def __next__(self):
        if self.NameThread[-1] != "#":  # Хитрость для поодержки итерации
            self.NameThread += "#"
            return self
        else:
            self.NameThread = self.NameThread[:-1:]
            raise StopIteration

    def is_lock(self):
        raise NotImplementedError()


# Синхронизация потоков в порядке очереди
class SyncModDataSkippIterQueue(SyncModData):
    """
    Цель:
        Синхронизайия доступа потоковна к общим ресурасм системы

    Особености:
        - Потоки не блокируються, а продолжабт работу по сбору данных.

    Возможности:
        - Ограничивает доступ потоков к внешним ресурасм путем
        - организации строгой очереди. Первый зашел последним вывышел.

    От автора:
        Если ваши потоки работает с приблизительно одинаковами
        размерами данных то этот лучший выбор для синхронизации достпуа к ресурасам.

    """

    LockAllThread: list = [False]  # Глабальная Ссылка видная всем потокам
    LockList: List[int] = []  # Массив по правилам Очереди
    DEBUG_INFO: bool = False  # Отображать штформации о потоках

    # Пример использования
    """
    from SyncThread.sync_mod_data import SyncModDataSkippIterQueue
    SyncModDataSkippIterQueue.DEBUG_INFO = True
    
    def ExampleFun(item_thread: SyncModDataSkippIterQueue) -> None:
        global data
        for x in range(1, 100):
            # Если Lock свободен и поток первый в очереди -> 
            # то устанавливаем Lock для других потоков и проходим на запись
            if item_thread.is_lock():   


                print(f"[MOD DATA]\t\t{item_thread}: {data}")
                data += 1

                
                item_thread(lock=False)
                # Снимаем Lock для всех потоков, но доступ на запись только в порядке очереди
            else:
                continue
                
    threadList = []

    nameList = [SyncModDataSkippIterQueue("Th_1"),
                SyncModDataSkippIterQueue("Th_2"),
                SyncModDataSkippIterQueue("Th_3"),
                SyncModDataSkippIterQueue("Th_4"),
                SyncModDataSkippIterQueue("Th_5"),
                ]
    #
    for th in nameList:
        tmp = threading.Thread(target=ExampleFun, args=(th))
        threadList.append(tmp)
        tmp.start()
    #
    for th in threadList:
        th.join()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.__id = id(self)
        self.__LockThread: list = SyncModDataSkippIterQueue.LockAllThread  # Связываем сслыки
        SyncModDataSkippIterQueue.LockList.append(id(self))  # Образуем очередь из потоков

    # Проверить разрешение потока на запись
    def is_lock(self) -> bool:
        if self.__id == SyncModDataSkippIterQueue.LockList[0]:
            SyncModDataSkippIterQueue.LockAllThread = [True]  # Поменял местами
            if SyncModDataSkippIterQueue.DEBUG_INFO:
                print(f"[INFO]\t\t\t{self}: Lock Write")
            return True  # Если поток находиться в начале очереди то допусктить, иначе поток пропускает итерацию
        else:
            return False

    # Закрыть или откртыть доступ к записи
    def __call__(self, *, lock: bool):
        if not lock:  # Есси поток занял очередь -> Переносим поток в конец очерди
            if SyncModDataSkippIterQueue.DEBUG_INFO:
                print(f"[INFO]\t\t\t{self}: UnLock Write")
            SyncModDataSkippIterQueue.LockList.append(SyncModDataSkippIterQueue.LockList.pop(0))
            SyncModDataSkippIterQueue.LockAllThread = [False]

    @property
    def LockThread(self) -> bool:
        return self.__LockThread[0]

    @LockThread.setter
    def LockThread(self, *, lock_all_thread: bool):
        SyncModDataSkippIterQueue.LockAllThread = lock_all_thread


class SyncModDataSkippIterSortQueue(SyncModData):
    """
    Цель:
        Класс для синхронизации доступа потокв к (глабальным данным, файлам, общих ресурасм).

    Возможнотси:
        - Класс позволяет организовать очередь у потоков к внешним ресурсам
        - Класс контралирует размер данных в потоке и сортирует порядок очереди
        таким образом, что потоки которые имеют больший размер данных получают приоритет на доступ к ресурсам.

    Особености:
        - Потоки не блокируються, а продолжабт работу по сбору данных.
        - Нет строгой очереди

    От автора:
        Думаю есть сымсл использовать этот класс синхронизации для
        потоков которые с большой вероятносятью могут быть по разному нагруженны
        и чтобы ОЗУ в первую очередь освобожждалась
        от больших данных
    """
    LockAllThread: list = [False]  # Глабальная Ссылка видная всем потокам
    LockListSort: \
        List[Union[
            int, List]] = []  # Массив в виде справедливой очереди, порядок сортируеться с учетом размерра данных у потоках
    DEBUG_INFO: bool = False  # Отображать инфорамию о потках

    # Пример использования
    """
    from SyncThread.sync_mod_data import SyncModDataSkippIterSortQueue
    SyncModDataSkippIterSortQueue.DEBUG_INFO = True
    
    def testTherad(item_thread: SyncModDataSkippIterSortQueue) -> None:
        new_data: list = []
        item_thread.SetData(LinkDataThread=new_data)
        for x in range(100):
            if item_thread.is_lock():

                print(f"[MOD DATA]\t\t{item_thread}: {getsizeof(new_data)}")
                print(SyncModDataSkippIterSortQueue.LockListSort)

                new_data.clear()

                time.sleep(3)
                item_thread(lock=False)
            else:
                time.sleep(random.uniform(0.1, 4.2))
                new_data.append(1)
                continue
                
    
    if __name__ == '__main__':
        threadList = []
        nameList = [SyncModDataSkippIterSortQueue("Th_1"),
                    SyncModDataSkippIterSortQueue("Th_2"),
                    SyncModDataSkippIterSortQueue("Th_3"),
                    SyncModDataSkippIterSortQueue("Th_4"),
                    SyncModDataSkippIterSortQueue("Th_5"),
                    ]
        #
        for th in nameList:
            tmp = threading.Thread(target=Test_SyncModDataSkippIterSortQueue.TheradFun, args=(th))
            threadList.append(tmp)
            tmp.start()
        #
        for th in threadList:
            th.join()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.__idThread = id(self)
        self.__LockThread: list = SyncModDataSkippIterSortQueue.LockAllThread  # Связываем сслыки
        SyncModDataSkippIterSortQueue.LockListSort.append([id(self)])  # [ [ id ,[link_data ], ... , ... ]

    def SetData(self, *, LinkDataThread: list):
        # Контролироуем размер данных собираем ссылки на данные
        for it in SyncModDataSkippIterSortQueue.LockListSort:
            if it[0] == self.__idThread:
                it.append(LinkDataThread)  # Сохраняем ссылки на данные

    # Проверить разрешение потока на запись
    def is_lock(self) -> bool:
        if self.__idThread == SyncModDataSkippIterSortQueue.LockListSort[0][0]:
            SyncModDataSkippIterSortQueue.LockAllThread = [True]
            if SyncModDataSkippIterSortQueue.DEBUG_INFO:
                print(f"[INFO]\t\t\t{self}: Lock Write")
            return True
        else:
            return False

    # Закрыть или откртыть доступ к записи
    def __call__(self, *, lock: bool):
        if not lock:  # Есси поток занял очередь -> Переносим поток в конец очерди
            if SyncModDataSkippIterSortQueue.DEBUG_INFO:
                print(f"[INFO]\t\t\t{self}: UnLock Write")
            try:
                # Сортируем LockListSort
                SyncModDataSkippIterSortQueue.LockListSort = sorted(
                    SyncModDataSkippIterSortQueue.LockListSort, key=lambda it: getsizeof(it[1]), reverse=True)
                SyncModDataSkippIterSortQueue.LockAllThread = [False]
            except IndexError:
                raise IndexError("Обезательно укажите для всех потоков данные с которыми они работают"
                                 "\nЧерез команду:\n>> item_thread.SetData(LinkDataThread=new_data)")

    @property
    def LockThread(self) -> bool:
        return self.__LockThread[0]

    @LockThread.setter
    def LockThread(self, *, lock_all_thread: bool):
        SyncModDataSkippIterSortQueue.LockAllThread = lock_all_thread


class SyncModDataPauseIterQueue(SyncModData):
    """
    Останавливает работу все потков пока не будет открыт доступ на запись
    """
    LockAllThread: list = [False]  # Глабальная Ссылка видная всем потокам
    LockList: List[int] = []  # Массив по правилам Очереди
    DEBUG_INFO: bool = False  # Отображать штформации о потоках

    def __init__(self, name: str):
        super().__init__(name)
        self.__id = id(self)
        self.__LockThread: list = SyncModDataPauseIterQueue.LockAllThread  # Связываем сслыки
        SyncModDataPauseIterQueue.LockList.append(id(self))  # Образуем очередь из потоков

        # Проверить разрешение потока на запись

    def is_lock(self) -> bool:
        # Ждать потоку пока не будет открыто на запись
        while self.__LockThread:
            if self.__id == SyncModDataPauseIterQueue.LockList[0]:
                SyncModDataPauseIterQueue.LockAllThread = [True]  # Поменял местами
                if SyncModDataPauseIterQueue.DEBUG_INFO:
                    print(f"[INFO]\t\t\t{self}: Lock Write")
                return True  # Если поток находиться в начале очереди то допусктить, иначе поток пропускает итерацию
            else:
                time.sleep(random.uniform(0.2, 1.1))

    def __call__(self, *, lock: bool):
        if not lock:  # Есси поток занял очередь -> Переносим поток в конец очерди
            if SyncModDataPauseIterQueue.DEBUG_INFO:
                print(f"[INFO]\t\t\t{self}: UnLock Write")
            SyncModDataPauseIterQueue.LockList.append(SyncModDataPauseIterQueue.LockList.pop(0))
            SyncModDataPauseIterQueue.LockAllThread = [False]

    @property
    def LockThread(self) -> bool:
        return self.__LockThread[0]

    @LockThread.setter
    def LockThread(self, *, lock_all_thread: bool):
        SyncModDataPauseIterQueue.LockAllThread = lock_all_thread


if __name__ == '__main__':
    pass
