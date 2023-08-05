# coding=utf-8

import allure
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DbSteps(object):
    def __init__(self, config):
        self.host = config.mysqlhost
        self.user = config.mysqluser
        self.password = config.mysqlpassword
        self.engine = create_engine('mysql+mysqldb://' + self.user + ':' + self.password
                                    + '@' + self.host + '/' + config.mysqldb + '?charset=utf8', echo=False)

    @allure.step("Запрашивает первую запись из таблицы '{1}' согласно критерию '{2}'")
    def query_first(self, table, filter_):
        """
        Выборка первой записи по указанному фильтру из таблицы
        :param table: класс из db/qsystem.py который представляет таблицу БД
        :param filter_: фильтр данных из таблицы
        :return: первый результат запроса (заполненный 'table' инстанс) или None если резутат не содержит записей.
        Example: user.query_first(History, History.mobile_phone == '3456774')
        """
        s = sessionmaker(bind=self.engine, expire_on_commit=False)()
        result = s.query(table).filter(filter_).first()
        s.close()
        return result

    @allure.step("Запрашивает все записи из таблицы '{1}' согласно критерию '{2}'")
    def query_all(self, table, filter_):
        """
        Выборка всех записей по указанному фильтру из таблицы
        :param table: класс из db/qsystem.py который представляет таблицу БД
        :param filter_: фильтр данных из таблицы
        :return:
        Example: user.query_all(Advance, Advance.advance_time.like('2015-10-08%'))
        """
        s = sessionmaker(bind=self.engine, expire_on_commit=False)()
        results = s.query(table).filter(filter_).all()
        s.close()
        return results

    @allure.step
    def add(self, params):
        """
        Добавление данных в таблицу
        :param params: класс из db/qsystem.py содержащий данные таблицы БД
        :return:
        Example: user.add(users.OPERATOR.customers_data)
        """
        s = sessionmaker(bind=self.engine, expire_on_commit=False)()
        s.add(params)
        s.commit()
        s.close()

    @allure.step
    def update(self, table, filter_, params):
        """
        Обновление данных в таблице базы данных
        :param table: класс из db/qsystem.py который представляет таблицу БД
        :param filter_: фильтр данных из таблицы
        :param params: параметры с новыми данными, например {"name": 'new_name'}
        :return: количество строк которые были обновлены
        """
        s = sessionmaker(bind=self.engine, expire_on_commit=False)()
        result = s.query(table).filter(filter_).update(params)
        s.commit()
        s.close()
        return result

    @allure.step
    def delete(self, table, filter_):
        """Удаление записи(ей) из таблицы
        :param table: класс из db/qsystem.py который представляет таблицу БД
        :param filter_: фильтр данных из таблицы
        :return:
        Example: user.delete(Customers, Customers.id == 3)
        """
        s = sessionmaker(bind=self.engine)()
        s.delete(self.query_first(table, filter_))
        s.commit()
        s.close()
