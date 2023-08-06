"""
    Класс отвевечает за создание подключения к БД PostgreSQL
    и является менеджером соединений.

    Классы работающие с БД его наследуют
"""
import hashlib
import logging
import random
import time

import psycopg2
import psycopg2.extras
import re

query_replace = re.compile('(%s)')

class SynchronousConnector:

    def __init__(self, config):
        """
            Конструктор парсит настройки БД.
            В качестве метода ожидаем конфиг с настройками
        """
        # Храним настройки соединения с БД
        self._db_config = None

        # Словарь для подготовленных выражений
        self._prepared_statements = {}

        # Максимальный таймаут перед попытками подключения (сек)
        self._max_timeout = 60

        if self._db_config is None: self._db_config = {}

        self._connection = None

        self._db_config = {
            'host': config['host'],
            'user': config['user'],
            'password': config['password'],
            'port': config['port'],
            'database': config['database'],
        }

    def get_connector(self):
        """
            Метод возвращает дескриптор подключения.
            Коннектор принимает специальный параметр: ctype - тип коннентора.
            Это необходимо, чтобы разделить коннектор для прослушивания "оповещений" и выполнения запросов.
        """

        # Проверяем наличие существующего соединения
        # Если нет - устанавливаем
        # Дескриптора соединения
        if self._connection is None:

            while True:
                # Количество попыток соединения
                number_of_connection_attempts = 0

                try:
                    self._connection = psycopg2.connect(**self._db_config).cursor(
                        cursor_factory=psycopg2.extras.DictCursor)
                    self._connection.connection.set_isolation_level(
                        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

                    return self._connection

                except Exception as e:
                    logging.warning('Ошибка подключения к СУБД PostgreSQL. Ошибка: %s' % (str(e)))

                # Обрабатываем ошибку подключения
                number_of_connection_attempts += 1

                if number_of_connection_attempts > self._max_timeout:
                    timeout = self._max_timeout
                else:
                    timeout = random.randint(1, number_of_connection_attempts)

                time.sleep(timeout)

        # В случае когда отправлена задача: завершения работы демона - вызываем исключение
        if self._connection is None: raise Exception('Получен сигнал завершения')

        # Десприптор соединяния есть. Проверяем состояние - активно ли соединение
        if self._connection.closed is True:
            # Сбрасываем дескриптор соединения и пытаемся подключиться
            self._connection = None
            return self.get_connector()

        return self._connection

    def query(self, query, data=None):
        """
        Метод осуществляет запрос к БД.
        Запросы надо отправлять через этот метод по следующим причинам:
          - в случае разрыва соединения - пытается поднять соединение и отправить запрос еще раз
          - запоминает подготовленные запросы и использует их - уменьшая издержки
        """
        query_hash = hashlib.sha1(query.encode('utf-8')).hexdigest()

        try:
            return self._prepared_statements[query_hash](data)

        # Очищаем список подготовленных выражений в случае разрыва соединения
        # Заново создаем подключение
        except KeyError:
            self._prepared_statements[query_hash] = self._prepare(query=query, name=query_hash)
            return self._prepared_statements[query_hash](data)

    def _prepare(self, query, name):
        """ Подготавливаем выражение """

        i = 1
        for n in query_replace.findall(query):
            query = query.replace('%s', '$%s' % i, 1)
            i += 1

        query = """PREPARE pquery_%s AS %s""" % (name, query)
        self.get_connector().execute(query)

        def inner(data=None):
            """ Внутренняя функция, которая отвечает за данный подготовленный запрос """
            if data is None or len(data) == 0:
                self.get_connector().execute('EXECUTE pquery_%s;' % name)
                return self.get_connector()
            else:
                self.get_connector().execute('EXECUTE pquery_%s(%s);' % (name, str(','.join(['%s'] * len(data)))), data)
                return self.get_connector()

        return inner
