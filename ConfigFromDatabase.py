# -*- coding: UTF-8 -*-
import time
from LoggerModule import Logger
from ConfigManager import ConfigParameter as configs
from DatabaseConnectionPool import DatabaseConnectionPool as db_pool
import DatabaseInterface


def reload_config_from_database():
    while (True):
        database_connection = None
        try:
            database_connection = db_pool.get_connection()
            ConfigFromDatabase.load_config_from_database(database_connection)

        except Exception as e:
            Logger.error("when reload configurations from database!")
            Logger.error(repr(e))
            if database_connection is not None:
                try:
                    database_connection.close()
                except Exception as e2:
                    Logger.error('when try to close the database connection after error during reloading configurations from database.')
                    Logger.error(repr(e2))

        database_connection.close()
        Logger.info('Thread to reload config from database keeps alive.')
        time.sleep(configs.reload_config_from_database_interval)


class ConfigFromDatabase:
    database_version = 'ZhengTai-B1.1-V4.0.0.0.0'
    @classmethod
    def load_config_from_database(cls, database_connection):
        # 这里从数据库中读取所有配置参数
        #
        rows, error_info = DatabaseInterface.execute_commit_sql(database_connection, "select 1")
        if error_info is not None:
            Logger.error('cannot load configuration from the database since the SQL execution fails.')
            return cls

        configs.configs_from_database = cls

        return cls

