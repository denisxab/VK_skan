import json
import os
import re
import time
from tkinter import *

import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import Soport_webdriver


class SeeUser:
    def __init__(self, name_file: str, userName: str, password: str, view_favorite_profiles: bool):

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        self.b = webdriver.Chrome(
            desired_capabilities=caps, executable_path="chromedriver.exe")
        self.openvk(userName, password)
        a = Soport_webdriver.CLR_Html(self.b,
                                      ['page_name', 'profile_message_send', 'profile_action_btn', 'profile_msg_split'])
        print(a)

        self.label = name_file
        self.vk_clr = self.Read_Json_User(view_favorite_profiles)

        self.i = -1
        self.p = len(self.vk_clr)
        self.windowTk = Tk()
        self.windowTk.geometry('{}x{}'.format('380', '450'))

        frame1 = Frame(self.windowTk)
        bat0 = Button(frame1, width=10, text='>',
                      bg='#4E51D8', command=self.right)
        bat1 = Button(frame1, width=10, text='<',
                      bg='#4E51D8', command=self.left)
        bat2 = Button(frame1, width=10, text='SV', command=self.on_closed)
        bat3 = Button(self.windowTk, width=10, text='Написать',
                      command=self.set_message)
        bat4 = Button(self.windowTk, width=10,
                      text='favorite', command=self.favorite)

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

    def Read_Json_User(self, Lik=bool) -> list:
        vk_clr = []
        if not Lik:
            name1 = '{}\\userId.json'.format(self.label)
            name2 = '{}\\userId_1.json'.format(self.label)

            if 'userId_1.json' in os.listdir('{}\\'.format(self.label)):
                with open(name2, 'r') as file_json:
                    vk_clr = json.load(file_json)

            else:
                with open(name1, 'r') as file_json:
                    vk_clr = []
                    for x in json.load(file_json):
                        vk_clr.append(x[0])
                    with open(name2, 'w') as file_json:
                        json.dump(vk_clr, file_json)

        elif Lik:
            name2 = 'favorite.json'
            with open(name2, 'r') as file:
                vk_clr = json.load(file)

        return vk_clr

    def openvk(self, userName: str, password: str):
        try:
            self.b.get('https://vk.com/im')
            self.b.find_element_by_id('email').send_keys(userName)
            self.b.find_element_by_id('pass').send_keys(password)
            self.b.find_element_by_id('login_button').click()
            time.sleep(1)
        except NameError:
            self.b.find_element_by_name("box_x_button").click()

    def right(self, garbageBindTkinter=0):


        if self.i < len(self.vk_clr)-1:
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
            self.i = len(self.vk_clr)-1

        self.lab0['text'] = '{}\n-{}-'.format(
            self.vk_clr[self.i], self.p - self.i)
        self.windowTk.update()
        self.b.get('https://vk.com/id{}'.format(self.vk_clr[self.i]))



    def on_closed(self):
        name2 = '{}\\userId_1.json'.format(self.label)
        with open(name2, 'w') as file_json:
            json.dump(self.vk_clr[self.i:], file_json)

        self.windowTk.destroy()
        self.b.close()

    def set_message(self):
        try:
            with open('text_mail.txt', 'r') as file_text:
                tExt_send_massage = ' '.join(re.findall(
                    re.compile('[^\n]+'), file_text.read()))
                name_user_set_massage = self.b.find_element_by_class_name(
                    'page_name').text.split(' ')[0]

                try:
                    self.b.find_element_by_id('profile_message_send').click()
                except selenium.common.exceptions.ElementNotInteractableException:
                    self.b.get(
                        'https://vk.com/id{}'.format(self.vk_clr[self.i]))
                    self.b.find_element_by_id('profile_message_send').click()

                self.b.find_element_by_id('mail_box_editable').send_keys(
                    'Привет {}, {}'.format(name_user_set_massage, tExt_send_massage))

        except FileNotFoundError:
            print("Нет файла text_mail.txt")

        # b.find_element_by_id('mail_box_send').click()

    def favorite(self):
        self.lab0['text'] = '||||||||||||||||||||||||||||||||||'
        self.windowTk.update()
        try:
            with open('favorite.json', 'r') as file_json:
                lls = json.load(file_json)
                lls.append(self.vk_clr[self.i])

            with open('favorite.json', 'w') as file_json:
                json.dump(lls, file_json)

        except FileNotFoundError:
            with open('favorite.json', 'w') as file_json:
                list_q = [self.vk_clr[self.i]]
                json.dump(list_q, file_json)






if __name__ == "__main__":
    name_group = "tproger"

    dt = data_private()
    SeeUser(name_file=name_group,
            userName=dt["name"],
            password=dt["password"],
            view_favorite_profiles=False)
