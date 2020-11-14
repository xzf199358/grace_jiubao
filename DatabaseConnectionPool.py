# -*- coding: UTF-8 -*-

import sys
import psycopg2
from LoggerModule import Logger
from ConfigManager import ConfigParameter as configs
from DBUtils.PooledDB import PooledDB
import ToolFunctions


class DatabaseConnectionPool:
    pool = None

    @classmethod
    def create_pool(cls):
        try:
            cls.pool = PooledDB(psycopg2, maxconnections = configs.max_connection_num,
                                mincached = configs.min_cached_num, maxcached = configs.max_cached_num,
                                maxshared = configs.max_shared_num, application_name = configs.application_name_for_database_connection,
                                host = configs.database_host, port=configs.database_port, dbname = configs.database_name,
                                user = configs.database_user_name, password=configs.database_password)
            return cls

        except Exception as e:
            Logger.fatal("failed to initialize Database Connection Pool. System is exiting!")
            Logger.fatal(repr(e))
            ToolFunctions.sys_exit(301)

    @classmethod
    def get_connection(cls):
        try:
            return cls.pool.connection()
        except Exception as e:
            Logger.error("when get connection from pool!")
            Logger.error(repr(e))
            return None

    @classmethod
    def get_dedicated_connection(cls): # 专用连接：数据库服务端一个专有进程处理该连接，相对于共享连接而言
        try:
            return cls.pool.dedicated_connection()
        except Exception as e:
            Logger.error("when get dedicated connection from pool!")
            Logger.error(repr(e))
            return None

# db_pool = DatabaseConnectionPool

