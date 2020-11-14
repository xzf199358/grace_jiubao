# -*- coding: UTF-8 -*-
# this module is to load configurations

import os
import sys
import configparser
from version import program_version_no
import ToolFunctions


class ConfigParameter:
    database_host = 'localhost'
    database_port = '5432'
    database_name = 'postgres'
    database_user_name = 'postgres'
    database_password = '123456'

    reload_config_from_database_interval = 5

    max_connection_num = 6
    min_cached_num = 5
    max_cached_num = 5
    max_shared_num = 5
    application_name_for_database_connection = 'General Dispatch'
    blocking = False

    logger_name = 'root'

    configs_from_database = None  # 所有从数据库里读取的配置项
    return_to_zero_interval = 10

    valid_data_threshold_time = 8
    invalid_data_threshold_time = 480

    data_package_id = 0

    @classmethod
    def load_config(cls):
        config_file_path = ''
        try:
            current_path = os.getcwd()
            config_file_path = current_path + "\config\config.ini"
            print('loading config file at path: ' + config_file_path)
            config_reader = configparser.ConfigParser()
            config_reader.read(config_file_path)

            load_public_config_result = cls.load_public_config()
            if not load_public_config_result:
                cls.database_host = config_reader.get('database_connection', 'host')
                cls.database_port = config_reader.get('database_connection', 'port')
                cls.database_name = config_reader.get('database_connection', 'database_name')
                cls.database_user_name = config_reader.get('database_connection', 'user_name')
                cls.database_password = config_reader.get('database_connection', 'password')

            cls.reload_config_from_database_interval = config_reader.getfloat('reload_config_from_database','update_interval') # unit: seconds

            cls.max_connection_num = config_reader.getint('database_connection_pool', 'max_connection_num')
            cls.min_cached_num = config_reader.getint('database_connection_pool', 'min_cached_num')
            cls.max_cached_num = config_reader.getint('database_connection_pool', 'max_cached_num')
            cls.max_shared_num = config_reader.getint('database_connection_pool', 'max_shared_num')
            cls.application_name_for_database_connection = config_reader.get('database_connection_pool', 'application_name_for_database_connection')
            cls.application_name_for_database_connection += '_' + program_version_no
            cls.blocking = config_reader.getboolean('database_connection_pool', 'blocking')

            cls.blocking = config_reader.getboolean('database_connection_pool', 'blocking')

            cls.return_to_zero_interval = config_reader.getfloat('tcp_connect_config', 'return_to_zero_interval')
            cls.valid_data_threshold_time = config_reader.getfloat('tcp_connect_config', 'valid_data_threshold_time')
            cls.invalid_data_threshold_time = config_reader.getfloat('tcp_connect_config', 'invalid_data_threshold_time')
            cls.data_package_id = config_reader.getint('tcp_connect_config', 'data_package_id')
            from GlobalContext import DispatchContext
            DispatchContext.data_package_id = (int(cls.data_package_id) + 10) % 10000
            return cls

        except Exception as e:
            # 注意，由于需要先加载配置，后启动logging模块，所以这里还不能使用logger.error()
            print('Error: failed to read configuration file! File path should be at: ' + config_file_path)
            print(repr(e))

            file_start_log = open('./log/start.log','w')
            file_start_log.write('Error: failed to read configuration file! File path should be at: ' + config_file_path
                                 + '\r\n' + str(repr(e)))
            file_start_log.close()

            ToolFunctions.sys_exit(201) # fatal error, need exit the program

    @classmethod
    def load_public_config(cls) -> bool:  # return True meaning success and False meaning failure
        try:
            current_path = os.getcwd()
            config_file_path = os.path.dirname(current_path) + "/public_database_connection.config"
            print('loading public config file at path: ' + config_file_path)
            if not os.path.exists(config_file_path):
                raise Exception('public config file does not exist!')

            config_reader = configparser.ConfigParser()
            config_reader.read(config_file_path)
            cls.database_host = config_reader.get('database_connection', 'host')
            cls.database_port = config_reader.get('database_connection', 'port')
            cls.database_name = config_reader.get('database_connection', 'database_name')
            cls.database_user_name = config_reader.get('database_connection', 'user_name')
            cls.database_password = config_reader.get('database_connection', 'password')
            return True  # success

        except Exception as e:
            print('encountered exception when load_public_config(): ' + repr(e))
            print('Warning!!! try to load public configuration file failed! file should be at: ./../public_database_connection.config')
            print('will try to load configuration file from ./config/config.ini instead.')
            return False  # failed


# configs = ConfigParameter

