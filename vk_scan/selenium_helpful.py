from logsmal import logger
from selenium import webdriver


class Browser:
    """
    Работа с браузером
    """

    def __init__(self, executable_path, options=None):
        """
        path_to_driver: Путь к драйверу селениума 
        options: Опции для браузера
        """
        self.driver = webdriver.Firefox(
            executable_path=executable_path,
            options=options
        )

    def close_browser(self):
        """
        Закрыть окно браузера
        """
        self.driver.close()
        self.driver.quit()


def get_browser(browser_: Browser):
    def inerr(func):
        def wraper(*args, **kwargs):
            try:
                func(*args, browser=browser_, **kwargs)
            except Exception as e:
                logger.error(str(e), 'get_browser')
                browser_.close_browser()
        return wraper
    return inerr
