# coding=utf-8
from time import sleep

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from hamcrest import assert_that, equal_to, is_, not_none, none, contains_string, equal_to_ignoring_case
import selenium.webdriver.support.expected_conditions as ec


class UserSteps(object):
    def __init__(self, config):
        self.config = config
        self.driver = config.driver
        self.element_wait = config.element_wait

    @allure.step("Открывает страницу '{1}'")
    def opens(self, url):
        self.driver.get(str(url))

    @allure.step("Проверяет наличие элемента '{1}' на странице")
    def should_see_element(self, element):
        assert_that(element.element, not_none(), u'Элемент отсутствует на странице ' + self.driver.current_url)

    @allure.step("Проверяет отсутствие элемента '{1}' на странице")
    def should_not_see_element(self, element):
        assert_that(element.element, none(), u'Элемент присутствует на странице ' + self.driver.current_url)

    @allure.step("Проверяет значение '{3}' атрибута '{2}' у элемента '{1}'")
    def should_see_attribute_value(self, element, attribute, value):
        if 'Input' in str(element.__class__):
            element_ = element.input
        else:
            element_ = element.element

        element_attribute = element_.get_attribute(attribute)
        assert_that(element_attribute, not_none(), u'Атрибут отсутствует у элемента')
        assert_that(element_attribute, equal_to_ignoring_case(str(value)),
                    u'Значение атрибута ' + attribute + ' не соответствует ожидаемому')

    @allure.step("Ожидает исчезновение элемента '{1}'")
    def waits_for_element_disappeared(self, element):
        try:
            WebDriverWait(self.driver, self.element_wait).until_not(
                lambda s: self.driver.find_element(element.by, element.locator).is_displayed())
        except TimeoutException:
            assert_that(not TimeoutException, u'Элемент не должен присутствовать в верстке страницы '
                        + self.driver.current_url)

    @allure.step("Ожидает появление элемента '{1}'")
    def waits_for_element_displayed(self, element):
        try:
            WebDriverWait(self.driver, self.element_wait).until(
                lambda s: self.driver.find_element(element.by, element.locator).is_displayed())
            return element
        except TimeoutException:
            assert_that(not TimeoutException, u'Элемент не отображается на странице '
                        + self.driver.current_url)

    @allure.step("Текст элемента '{1}' соответствует '{2}'")
    def should_see_element_with_text(self, element, text):
        assert_that(element.element.text, equal_to(str(text)), u'Текст не соответствует ожидаемому значению')

    @allure.step("Элемента '{1}' соответствует '{2}'")
    def should_see_element_matched_to(self, element, matcher):
        assert_that(element.element.text, matcher, u'Параметры элемента не соответствует ожидаемому значению')

    @allure.step("Текст ошибки '{1}' соответствует '{2}'")
    def should_see_field_error_text(self, input_, text):
        try:
            WebDriverWait(self.driver, self.element_wait)\
                .until(lambda x: input_.error).is_displayed()
        except TimeoutException:
            assert_that(False, u'Поле не отмечено как содержащее ошибку')

        assert_that(input_.error.text, contains_string(str(text)),
                    u'Текст ошибки не соответствует ожидаемому значению')

    @allure.step("Значение в поле '{1}' соответствует '{2}'")
    def should_see_field_value(self, input_, value):
        assert_that(input_.value, equal_to(str(value)),
                    u'Значение в поле не соответствует ожидаемому')

    @allure.step("Список '{1}' содержит '{2}' элемент(a/ов)")
    def should_see_list_size(self, multipleelement, size):
        assert_that(len(multipleelement.elements), is_(size), u'Список не содержит ожидаемое количество элементов')

    @allure.step("Нажимает элемент '{1}'")
    def clicks(self, element):
        try:
            e = WebDriverWait(self.driver, self.element_wait)\
                .until(ec.element_to_be_clickable((element.by, element.locator)))
            e.click()
        except TimeoutException:
            assert_that(element.element, not_none(), u'Невозможно нажать на элемент на странице '
                        + self.driver.current_url)

    @allure.step("Выбирает значение '{2}' из списка '{1}'")
    def chooses_from_select(self, select, value):
        select.select.select_by_visible_text(value)

    @allure.step("Выбирает пункт '{2}' из списка '{2}' по названию")
    def selects_from_list_by_text(self, list_, text):
        list_.get_element_contains_text(text).element.click()

    @allure.step("Выбирает пункт '{2}' из списка '{2}' по значению атрибута")
    def selects_from_list_by_attr_value(self, list_, attr, value):
        list_.get_element_by_attribute(attr, value).element.click()

    @allure.step("Ожидает '{1}' секунд(ы)")
    def waits_for(self, timeout=3):
        sleep(timeout)

    @allure.step("Вводит текст '{2}' в '{1}'")
    def enters_text(self, input_, text):
        if input_.__class__.__name__ == 'Input':
            input_.input.clear()
            input_.input.send_keys(text)
        else:
            input_.element.clear()
            input_.element.send_keys(text)

    @allure.step("Вводит текст '{2}' в '{1}'")
    def appends_text(self, input_, text):
        if input_.__class__.__name__ == 'Input':
            input_.input.send_keys(text)
        else:
            input_.element.send_keys(text)

    @allure.step("Ожидает завершения AJAX запроса")
    def waits_for_ajax(self):
        try:
            WebDriverWait(self.driver, self.element_wait).until(
                lambda s: s.execute_script('return $.active == 0'))
        except TimeoutException:
            assert_that(not TimeoutException, u'Истекло время ожидания AJAX запроса %s секунд'
                        % str(self.element_wait))

    @allure.step("Перегружает текущую страницу")
    def reloads_page(self):
        self.config.driver.refresh()
