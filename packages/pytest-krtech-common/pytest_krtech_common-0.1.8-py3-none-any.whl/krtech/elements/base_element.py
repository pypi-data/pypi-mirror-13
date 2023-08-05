# coding=utf-8
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


class BaseElement(object):

    def __init__(self, name, by, locator):
        self.__name = name
        self.__by = by
        self.__locator = locator
        self.__element = None

    @property
    def element(self):
        return self.__element

    @element.setter
    def element(self, value):
        self.__element = value

    @property
    def locator(self):
        return self.__locator

    @locator.setter
    def locator(self, value):
        self.__locator = value

    @property
    def by(self):
        return self.__by

    @by.setter
    def by(self, value):
        self.__by = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def __getitem__(self):
        return self

    def __str__(self):
        return self.__name

    def __get__(self, obj, owner):
        driver = obj.config.driver
        timeout = obj.config.element_wait
        time.sleep(obj.config.element_init_timeout)
        parent_element = obj.element

        try:
            WebDriverWait(driver, timeout).until(
                lambda s: parent_element.find_element(self.__by, self.__locator))
            self.__element = parent_element.find_element(self.__by, self.__locator)
            return self
        except TimeoutException:
            self.__element = None
            return self
