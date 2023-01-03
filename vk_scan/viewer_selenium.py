""" 
Отображение результата в селениуме
"""

from typing import Literal
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import threading
from tkinter import BOTH, Button, Frame, Label, Tk
from selenium.webdriver.remote.webelement import WebElement
from selenium_helpful import Browser
from selenium.webdriver.firefox.options import Options
from model_db import TUserVk
from mg_sql.sql_async.base import SQL
import asyncio
from model_db import LikeUser


class TkWindowManager:
    def __init__(self, root_browser):
        self.root_browser = root_browser

    def run(self):
        """
        Открыть окно текинтора для управления перемещения по профилям
        """
        self.windowTk = Tk()
        self.windowTk.geometry('{}x{}'.format('380', '450'))
        #
        frame1 = Frame(self.windowTk)
        bat0 = Button(frame1, width=10, text='>',
                      bg='#4E51D8', command=self.NextUser)
        bat1 = Button(frame1, width=10, text='<',
                      bg='#4E51D8', command=self.LastUser)
        bat2 = Button(frame1, width=10, text='Close', command=self.on_closed)
        bat3 = Button(self.windowTk, width=10, text='Написать',
                      command=self.set_message)
        bat4 = None
        match self.root_browser.type_view:
            case 'all':
                bat4 = Button(self.windowTk, width=10,
                              text='Поставить Лайк', command=self.Like)
            case 'like':
                bat4 = Button(self.windowTk, width=10,
                              text='Убрать Лайк', command=self.DeleteLike)
        #
        self.lab0 = Label(self.windowTk, height=5, width=10, text='--')
        self.lab0.pack(fill=BOTH, expand=True)
        #
        frame1.pack(fill=BOTH, expand=True)
        bat1.pack(side='left', fill=BOTH, expand=True)
        bat2.pack(side='left', fill=BOTH, expand=True)
        bat0.pack(side='left', fill=BOTH, expand=True)
        bat3.pack(fill=BOTH, expand=True)
        bat4.pack(fill=BOTH, expand=True)
        #
        self.windowTk.bind('<Right>', self.NextUser)
        self.windowTk.bind('<Left>', self.LastUser)
        #
        self.windowTk.protocol("WM_DELETE_self.windosTkW", self.on_closed)
        self.windowTk.wm_attributes('-topmost', 1)
        self._UpdateWindowTitle()
        self.windowTk.mainloop()

    def NextUser(self, garbageBindTkinter=0):
        """Перейти к прошлому пользователю"""
        # Переместить курсор
        if self.root_browser.select_index < len(self.root_browser.list_all_user_vk) - 1:
            self.root_browser.select_index += 1
        else:
            self.root_browser.select_index = 0
        # Обновить заголовок Текинтора
        self._UpdateWindowTitle()
        # Открыть URL с новым пользователем
        self.OpenProfileUser()

    def OpenProfileUser(self):
        """Открыть профиль пользователя по текущему USER_ID"""
        self.root_browser.browser.driver.get(
            'https://vk.com/id{0}'.format(self._GetUserId()))

    def LastUser(self, garbageBindTkinter=0):
        """Перейти к следующему пользователю"""
        # Переместить курсор
        if self.root_browser.select_index > 0:
            self.root_browser.select_index -= 1
        else:
            self.root_browser.select_index = len(
                self.root_browser.list_all_user_vk) - 1
        self._UpdateWindowTitle()
        # Открыть URL с новым пользователем
        self.OpenProfileUser()

    def Like(self, garbageBindTkinter=0):
        """Поставить лайк"""
        # Добавить пользователя в таблицу для лайков
        @SQL.get_session_decor
        async def _s(_session):
            await SQL.write_execute_raw_sql(
                _session, **LikeUser.addLike(self._GetUserId()))
            print('Лайк Записан')
            return True
        asyncio.run(_s())
        # Обновить титульник текинтора
        self.lab0['text'] = '||||||||||||||||||||||||||||||||||'
        self.windowTk.update()

    def DeleteLike(self, garbageBindTkinter=0):
        """Убрать лайк"""
        # Удалить пользователя из таблицу для лайков
        @SQL.get_session_decor
        async def _s(_session):
            await SQL.write_execute_raw_sql(
                _session, **LikeUser.deleteLike(self._GetUserId()))
            print('Лайк Удален')
            return True
        asyncio.run(_s())
        # Обновить титульник текинтора
        self.lab0['text'] = '||||||||||||||||||||||||||||||||||'
        self.windowTk.update()

    def set_message(self):
        """Отправка сообщения"""
        pass

    def on_closed(self):
        """Обработка закрытия окна"""
        
        self.windowTk.destroy()
        self.root_browser.browser.close()

    ################################################################
    # Утилиты
    ################################################################

    def _UpdateWindowTitle(self):
        """Обновить заголовок Текинтора"""
        self.lab0['text'] = '{}\n-{}-'.format(
            self.root_browser.list_all_user_vk[self.root_browser.select_index][
                'user_id'], self.root_browser.count_users - self.root_browser.select_index
        )
        self.windowTk.update()

    def _GetUserId(self):
        """Получить пользователя по текущему индексу"""
        return self.root_browser.list_all_user_vk[self.root_browser.select_index]['user_id']


class ViewSelenium:
    def __init__(
        self,
        user_name: str,
        password: str,
        list_all_user_vk: list[TUserVk],
        type_view: Literal['all', 'like'],
        path_to_driver: str,
        options: Options,
        path_to_browser: str = r'C:\Program Files\Mozilla Firefox\firefox.exe',
    ):
        """
        user_name: Имя для входа
        password:  Пароль  для входа
        path_to_driver: Путь к драйверу селениума
        list_all_user_vk: Спсиок пользователей которых нужно отобразить
        type_view: Тип отображения, все пользователи, или только отлайканые
        path_to_browser: Путь к браузеру
        options: Опции для браузера
        """
        self.type_view = type_view
        # Индекс текущего выбранного пользователя
        self.select_index = 0
        # Список всех пользователей которые нужно отображать
        self.list_all_user_vk = list_all_user_vk
        # Сколько пользователей для просмотра
        self.count_users = len(self.list_all_user_vk)
        ###################
        # Текинтор
        ###################
        # Создать окно Текинтора для управления перемещения по профилям пользователей
        # В отдельном потоке
        self.tk_windows = TkWindowManager(self)
        thread_TkWindowManager = threading.Thread(
            target=self.tk_windows.run, args=(), name="TkWindowManager", daemon=True
        )
        thread_TkWindowManager.start()
        ###################
        # Селениум
        ###################
        # Путь к Firefox
        options.binary_location = path_to_browser
        # Создаем окно браузера
        self.browser = Browser(executable_path=path_to_driver, options=options)
        # Входим в аккаунт ВК
        self._open_vk(user_name, password)
        thread_TkWindowManager.join()

    def _open_vk(self, userName: str, password: str):
        """
        Войти в аккаунт ВК
        """
        self.browser.driver.get('https://vk.com/feed')
        # Поле ввода логина или телефона
        input_login: WebElement = self.browser.driver.find_element_by_css_selector(
            '#index_email')
        if input_login:
            # Сфокусироваться на поле ввода логина
            input_login.click()
            # Ввод логина
            input_login.send_keys(userName)
            # Нажать кнопку Войти
            bt_enter = self.browser.driver.find_element_by_css_selector(
                'button.FlatButton:nth-child(5)')
            bt_enter.click()
            # Ждем загрузки элемента ввода пароля
            wait = WebDriverWait(self.browser.driver, 10)
            input_password: WebElement = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.vkc__Password__Wrapper > div:nth-child(1) > div:nth-child(1) > input:nth-child(1)')
            )
            )
            input_password.click()
            input_password.send_keys(password)
            # Нажать кнопку войти
            self.browser.driver.find_element_by_css_selector(
                '.vkuiButton__in').click()
            ##
            # Открыть первого пользователя из списка
            ##
            self.tk_windows.OpenProfileUser()
        else:
            raise Exception('Не найдено полле для ввода логина')
