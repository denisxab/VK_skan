import random
import threading
import time
import unittest

from SyncThread.sync_mod_data import *

SyncModDataSkippIterQueue.DEBUG_INFO = True
SyncModDataSkippIterSortQueue.DEBUG_INFO = True


class Test_SyncModDataSkippIter(unittest.TestCase):
    data = 1

    @staticmethod
    def TheradFunTest(item_thread: SyncModDataSkippIterQueue) -> None:
        for x in range(100):
            print("\t" * 10 + f"{item_thread}")
            if item_thread.is_lock():

                print(f"[MOD DATA]\t\t{item_thread}: {Test_SyncModDataSkippIter.data}")
                Test_SyncModDataSkippIter.data += 1
                time.sleep(3)

                item_thread(lock=False)
            else:
                time.sleep(2)
                continue

    @unittest.skip("Test_SyncModDataSkippIter")
    def test_all(self):
        """
        Этот класс должен допускать к записи по одному потоку в порядке очереди


        :return:
        """
        print(threading.enumerate())
        threadList = []

        nameList = [SyncModDataSkippIterQueue("Th_1"),
                    SyncModDataSkippIterQueue("Th_2"),
                    SyncModDataSkippIterQueue("Th_3"),
                    SyncModDataSkippIterQueue("Th_4"),
                    SyncModDataSkippIterQueue("Th_5"),
                    ]
        #
        for th in nameList:
            tmp = threading.Thread(target=Test_SyncModDataSkippIter.TheradFunTest, args=(th))
            threadList.append(tmp)
            tmp.start()
        #
        for th in threadList:
            th.join()


class Test_SyncModDataSkippIterSortQueue(unittest.TestCase):

    @staticmethod
    def TheradFun(item_thread: SyncModDataSkippIterSortQueue) -> None:

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

    # @unittest.skip("Test_SyncModDataSkippIter")
    def test_all(self):

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


if __name__ == '__main__':
    unittest.main()
