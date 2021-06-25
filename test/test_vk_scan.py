import unittest

from vk_scan import SearchUserInGroup, get_my_password, offset_thread


class Test_SearchUserInGroup(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        self.name_group = "https://vk.com/prog_life"
        self.token = get_my_password(r"C:\Users\denis\PycharmProjects\pythonProject11\config.txt")["token"]

        self.my_class = SearchUserInGroup(
            token=self.token,
            name_group=self.name_group,
            count_user_group=20000,
            count_thread=3,
            versionApi="5.131")

    def __del__(self):
        pass


class Test_Fun(unittest.TestCase):
    def test_offset_thread(self):
        self.assertEqual(offset_thread(69257, 3), [(0, 23085), (23086, 46170), (46171, 69257)])


if __name__ == '__main__':
    unittest.main()
