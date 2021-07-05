import random
import threading
import time
import unittest

from SyncThread.sync_mod_data import *

SyncModDataSkippIterQueue.DEBUG_INFO = True
SyncModDataSkippIterSortQueue.DEBUG_INFO = True
SyncModDataPauseIterQueue.DEBUG_INFO = True
"""
https://www.youtube.com/watch?v=AWX4JnAnjBE
https://youtu.be/nR8WhdcRJwM
https://www.youtube.com/watch?v=ZGfv_yRLBiY&list=PLlWXhlUMyooawilqK4lPXRvxtbYiw34S8
"""


class Test_SyncModDataSkippIter(unittest.TestCase):
    data = 1

    @classmethod
    def TheradFun(cls,item_thread: SyncModDataSkippIterQueue) -> None:
        for x in range(100):
            print("\t" * 10 + f"{item_thread}")
            if item_thread.is_lock():

                print(f"[MOD DATA]\t\t{item_thread}: {cls.data}")
                cls.data += 1
                time.sleep(3)

                item_thread(lock=False)
            else:
                time.sleep(2)
                continue


    @classmethod
    @unittest.skip("Test_SyncModDataSkippIter")
    def test_all(cls):
        threadList = []
        nameList = SyncModData.CreateThread(5, SyncModDataSkippIterQueue)
        #
        for th in nameList:
            tmp = threading.Thread(target=cls.TheradFun, args=th)
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


    @classmethod
    @unittest.skip("Test_SyncModDataSkippIter1")
    def test_all(cls):
        threadList = []
        nameList = SyncModData.CreateThread(5, SyncModDataSkippIterSortQueue)
        #
        for th in nameList:
            tmp = threading.Thread(target=cls.TheradFun, args=th)
            threadList.append(tmp)
            tmp.start()
        #
        for th in threadList:
            th.join()


class Test_SyncModDataPauseIterQueue(unittest.TestCase):
    data = 1
    @classmethod
    def TheradFun(cls,item_thread: SyncModDataPauseIterQueue) -> None:
        for x in range(100):
            print("\t" * 10 + f"{item_thread}")
            if item_thread.is_lock():

                print(f"[MOD DATA]\t\t{item_thread}: {cls.data}")
                cls.data += 1
                time.sleep(3)

                item_thread(lock=False)
            else:
                time.sleep(2)
                continue



    @classmethod
    #@unittest.skip("Test_SyncModDataSkippIter")
    def test_all(cls):
        threadList = []
        nameList = SyncModData.CreateThread(5, SyncModDataPauseIterQueue)
        #
        for th in nameList:
            tmp = threading.Thread(target=cls.TheradFun, args=th)
            threadList.append(tmp)
            tmp.start()
        #
        for th in threadList:
            th.join()

if __name__ == '__main__':
    unittest.main()
