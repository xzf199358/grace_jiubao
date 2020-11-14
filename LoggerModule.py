# -*- coding: UTF-8 -*-

import logging
import logging.config
import os
import sys
import traceback
import ToolFunctions

# log level:
#     FATAL：致命错误
#     CRITICAL：特别糟糕的事情，如内存耗尽、磁盘空间为空，一般很少使用
#     ERROR：发生错误时，如IO操作失败或者连接问题
#     WARNING：发生很重要的事件，但是并不是错误时，如用户登录密码错误
#     INFO：处理请求或者状态变化等日常事务
#     DEBUG：调试过程中使用DEBUG等级，如算法中每个循环的中间状态


class LoggerManager:
    logger_general = None
    logger_file_and_stream = None
    logger_file_only = None

    @classmethod
    def create_logger(cls):
        try:
            current_path = os.getcwd()
            log_config_file_path = current_path + '/config/logging.conf'
            log_path = current_path + '/log'

            if not os.path.exists(log_path):
                # 如果不存在log目录则创建
                try:
                    os.makedirs(log_path)
                except Exception as e:
                    print('Error: when create log directory!')
                    print(repr(e))

            conf_file_path = os.path.join(current_path, 'config/logging.conf')
            logging.config.fileConfig(conf_file_path)
            cls.logger_file_only = logging.getLogger('log01')
            cls.logger_file_and_stream = logging.getLogger('log02')
            cls.logger_general = cls.logger_file_and_stream
            return cls.logger_general

        except Exception as e2:
            print('Error: when initialize Logger!')
            print(repr(e2))

            file_start_log = open('./log/LoggerInitialization.log', 'w')
            file_start_log.write('Error: failed to initialize Logger!'
                                 + '\r\n' + str(repr(e2))
                                 + 'Fatal error, program is exiting...')
            file_start_log.close()

            ToolFunctions.sys_exit(401)


class Logger:

    @classmethod
    def debug(cls, log_content):
        try:
            return LoggerManager.logger_general.debug(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def info(cls, log_content):
        try:
            return LoggerManager.logger_general.info(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def warning(cls, log_content):
        try:
            return LoggerManager.logger_general.warning(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def warn(cls, log_content):
        try:
            LoggerManager.logger_general.error(traceback.format_stack())
            return LoggerManager.logger_general.warn(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def error(cls, log_content):
        try:
            if len(sys.exc_info()) > 0 and sys.exc_info()[0] is not None:
                LoggerManager.logger_general.error(traceback.format_exc())
            else:
                LoggerManager.logger_general.error('traceback to this error is None.')
            LoggerManager.logger_general.error(cls.format_stack())
            return LoggerManager.logger_general.error(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def critical(cls, log_content):
        try:
            traceback_result = traceback.format_exc()
            if traceback_result is not None:
                LoggerManager.logger_general.critical(traceback_result)
            else:
                LoggerManager.logger_general.critical('traceback to this critical error is None.')
            LoggerManager.logger_general.error(cls.format_stack())
            return LoggerManager.logger_general.critical(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def fatal(cls, log_content):
        try:
            traceback_result = traceback.format_exc()
            if traceback_result is not None:
                LoggerManager.logger_general.fatal(traceback_result)
            else:
                LoggerManager.logger_general.fatal('traceback to this fatal error is None.')
            LoggerManager.logger_general.error(cls.format_stack())
            return LoggerManager.logger_general.fatal(log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def online_debug(cls, log_content):
        try:
            print('[online_debug]' + log_content)
            return LoggerManager.logger_general.debug('[online_debug]' + log_content)
        except Exception as e:
            print('logging module encounter error, cannot write logs!!!')
            print(repr(e))
            pass

    @classmethod
    def format_stack(cls):
        stack_list = traceback.format_stack()
        format_result = 'call stack: \n'
        if len(stack_list) <= 1:
            return format_result

        for i in range(0, len(stack_list) - 1):
            format_result += str(i) + ': ' + str(stack_list[i])

        return format_result


