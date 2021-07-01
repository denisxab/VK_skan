import time
from tkinter import *
from typing import List

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from vk_scan import get_my_password, name_group

sys.path.append(r"C:\Users\denis\PycharmProjects\pall")
from sqlliteorm.sqlmodules import *
from sqlliteorm.sqllite_orm import *

print(10)


# Поиск элемента
def CLR_Html(browser: webdriver, Name: str) -> str:
    """
    a = CLR_Html(self.b, ['page_name', 'profile_message_send', 'profile_action_btn', 'profile_msg_split'])
    print(a)
    :param Name:
    :param browser:
    :return:
    """

    res = []
    all_res = []
    # a = Soport_webdriver.CLR_Html(b,['mail_box_send'])
    for name in Name:

        try:
            all_res.append(browser.find_element_by_id(name).text)
            res.append('find_element_by_id')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_name(name).text)
            res.append('find_element_by_name')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_xpath(name).text)
            res.append('find_element_by_xpath')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_link_text(name).text)
            res.append('find_element_by_link_text')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_partial_link_text(name).text)
            res.append('find_element_by_partial_link_text')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_tag_name(name).text)
            res.append('find_element_by_tag_name')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_class_name(name).text)
            res.append('find_element_by_class_name')
        except:
            pass

        try:
            all_res.append(browser.find_element_by_css_selector(name).text)
            res.append('find_element_by_css_selector')
        except:
            pass

    io = ''
    for x in range(len(res)):
        io += '{} |-| {} |-| {}\n'.format(str(Name[x]), str(res[x]), str(all_res[x]))
    return io


class SeeUser:
    def __init__(self, name_db: str, userName: str, password: str, view_favorite_profiles: bool):
        self.name_db = "group/{0}.db".format(name_db if name_db.find("https://vk.com/") == -1 else name_db[15::])
        self.name_table = "sorted_users"
        self.sq = SqlLiteQrm(self.name_db)
        self.sq.CreateTable("like_user", {"id_like": toTypeSql(int)})
        self.vk_clr = self.ReadDB(view_favorite_profiles)

        ViewSee(self.vk_clr, self.sq, userName, password)

    def ReadDB(self, Lik: bool) -> List[str]:
        if Lik:
            vk_clr = list(map(lambda x: x[0], self.sq.GetTable("like_user")))
            if len(vk_clr) == 0:
                raise IndexError("Таблциа 'like_user' пустая")
        else:
            vk_clr = list(map(lambda x: x[0], self.sq.GetTable(self.name_table)))
        return vk_clr

    def DeleteTableLikeUser(self):
        self.sq.DeleteTable("like_user")


class ViewSee:
    def __init__(self,
                 vk_clr: List[str],
                 sq: SqlLiteQrm,
                 userName: str,
                 password: str
                 ):
        self.vk_clr = vk_clr
        self.sq = sq

        self.i = -1
        self.p = len(self.vk_clr)

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        self.b = webdriver.Chrome(
            desired_capabilities=caps, executable_path="chromedriver.exe")
        self.__open_vk(userName, password)

    def __open_vk(self, userName: str, password: str):
        try:
            self.b.get('https://vk.com/im')
            self.b.find_element_by_id('email').send_keys(userName)
            self.b.find_element_by_id('pass').send_keys(password)
            self.b.find_element_by_id('login_button').click()
            time.sleep(1)

        except NameError:
            self.b.find_element_by_name("box_x_button").click()
        self.__windows()

    def __windows(self):
        self.windowTk = Tk()
        self.windowTk.geometry('{}x{}'.format('380', '450'))

        frame1 = Frame(self.windowTk)
        bat0 = Button(frame1, width=10, text='>',
                      bg='#4E51D8', command=self.right)
        bat1 = Button(frame1, width=10, text='<',
                      bg='#4E51D8', command=self.left)
        bat2 = Button(frame1, width=10, text='Close', command=self.on_closed)
        bat3 = Button(self.windowTk, width=10, text='Написать',
                      command=self.set_message)
        bat4 = Button(self.windowTk, width=10,
                      text='Like', command=self.favorite)

        self.lab0 = Label(self.windowTk, height=5, width=10, text='--')
        self.lab0.pack(fill=BOTH, expand=True)

        frame1.pack(fill=BOTH, expand=True)
        bat1.pack(side='left', fill=BOTH, expand=True)
        bat2.pack(side='left', fill=BOTH, expand=True)
        bat0.pack(side='left', fill=BOTH, expand=True)
        bat3.pack(fill=BOTH, expand=True)
        bat4.pack(fill=BOTH, expand=True)

        self.windowTk.bind('<Right>', self.right)
        self.windowTk.bind('<Left>', self.left)

        self.windowTk.protocol("WM_DELETE_self.windosTkW", self.on_closed)
        self.windowTk.wm_attributes('-topmost', 1)
        self.windowTk.mainloop()

    def favorite(self):
        self.sq.ExecuteTable("like_user", self.vk_clr[self.i])
        self.lab0['text'] = '||||||||||||||||||||||||||||||||||'
        self.windowTk.update()

    def right(self, garbageBindTkinter=0):
        if self.i < len(self.vk_clr) - 1:
            self.i += 1
        else:
            self.i = 0

        self.lab0['text'] = '{}\n-{}-'.format(
            self.vk_clr[self.i], self.p - self.i)
        self.windowTk.update()
        self.b.get('https://vk.com/id{}'.format(self.vk_clr[self.i]))

    def left(self, garbageBindTkinter=0):

        if self.i > 0:
            self.i -= 1
        else:
            self.i = len(self.vk_clr) - 1

        self.lab0['text'] = '{}\n-{}-'.format(
            self.vk_clr[self.i], self.p - self.i)
        self.windowTk.update()
        self.b.get('https://vk.com/id{}'.format(self.vk_clr[self.i]))

    def on_closed(self):
        self.windowTk.destroy()
        self.b.close()

    def set_message(self):
        pass
        # try:
        #     with open('text_mail.txt', 'r') as file_text:
        #         tExt_send_massage = ' '.join(re.findall(
        #             re.compile('[^\n]+'), file_text.read()))
        #         name_user_set_massage = self.b.find_element_by_class_name(
        #             'page_name').text.split(' ')[0]
        #
        #         try:
        #             self.b.find_element_by_id('profile_message_send').click()
        #         except selenium.common.exceptions.ElementNotInteractableException:
        #             self.b.get(
        #                 'https://vk.com/id{}'.format(self.vk_clr[self.i]))
        #             self.b.find_element_by_id('profile_message_send').click()
        #
        #         self.b.find_element_by_id('mail_box_editable').send_keys(
        #             'Привет {}, {}'.format(name_user_set_massage, tExt_send_massage))
        #
        # except FileNotFoundError:
        #     print("Нет файла text_mail.txt")
        # b.find_element_by_id('mail_box_send').click()


if __name__ == "__main__":
    name_group = name_group  # Можно изментять
    dt = get_my_password("config.txt")
    SeeUser(name_db=name_group,
            userName=dt["name"],
            password=dt["password"],
            view_favorite_profiles=False)
