import unittest

from vk_scan import SearchUserInGroup, get_my_password, offset_thread


class Test_SearchUserInGroup(unittest.TestCase):

    def setUp(self):
        self.name_group = "https://vk.com/prog_life"
        self.token = get_my_password(r"C:\Users\denis\PycharmProjects\pythonProject11\config.txt")["token"]
        self.my_class = SearchUserInGroup(
            token=self.token,
            name_group=self.name_group,
            limit_get_user_group=0,
            count_thread=3,
            versionApi="5.131")


    #@unittest.skip("showing class skipping")
    def test_init(self):
        self.my_class.show_table(limit_show=3, width_column=10)
        self.my_class.show_search(limit_show=3, width_column=10)
        print()


    @unittest.skip("showing class skipping")
    def test_search(self):
        self.my_class.search()
        self.my_class.get_cont_user_group()
        self.my_class.show_table(limit_show=3, width_column=10)
        self.my_class.show_search(limit_show=3, width_column=10)


    def test_offset_thread(self):
        self.assertEqual(offset_thread(69257, 3), [(0, 23085), (23086, 46170), (46171, 69257)])


if __name__ == '__main__':
    unittest.main()
