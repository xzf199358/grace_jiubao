# -*- coding: UTF-8 -*-
# this is the main program of Dispatch Logics

import time
import threading
import psutil

from version import program_version_no
import ConfigManager
import LoggerModule
import DatabaseConnectionPool
import ToolFunctions
from SqlCollection import SqlCollection

# 启动初始化
# 要先load config，因为logging模块也依赖于配置项
configs = ConfigManager.ConfigParameter.load_config()
LoggerModule.LoggerManager.create_logger()
Logger = LoggerModule.Logger
db_pool = DatabaseConnectionPool.db_pool = DatabaseConnectionPool.DatabaseConnectionPool.create_pool()
Logger.info('Current Program Version: ' + program_version_no)


# read config from database
# 先载入logging模块，然后才能从数据库加载配置，因为该函数需要logging
# start a thread to periodically update configurations from database
try:
    import ConfigFromDatabase
    configs_from_database = ConfigFromDatabase.ConfigFromDatabase.load_config_from_database(db_pool.get_connection())

    thread_reload_config_from_database = threading.Thread(target = ConfigFromDatabase.reload_config_from_database,
                                                          name = 'reload_config')
    thread_reload_config_from_database.setDaemon(True)
    thread_reload_config_from_database.start()
    Logger.info("start a new thread to call reload_config_from_database.")
except Exception as e:
    Logger.error("when start a new thread to reload config from database.")
    Logger.fatal(repr(e)) # use repr(e) instead of str(e), because repr(e) can show the exception type, while the str(e) can only show the args (may be None).
    ToolFunctions.sys_exit(101)

'''
初始化  数据库接口程序
'''
# read sql interface files
Logger.info('start to initialize sql interfaces from reading files...')
read_result = SqlCollection.load_sql_interfaces()
if read_result < 0:
    Logger.fatal('initialize_sql_interfaces encountered an exception!')
    ToolFunctions.sys_exit(105)
Logger.info('sql interfaces were initialized.')


'''
同步线程  主要 同步内存中的数据以及 数据库之间的数据 实时的从数据库中读取数据 以及
实时从内存中 写入到数据库中
'''
# start a thread to periodically synchronize data between the program memory and database
try:
    import DataSynchronization
    thread_synchronize_data = threading.Thread(target=DataSynchronization.synchronize_data,
                                             name = 'synchronize')
    thread_synchronize_data.setDaemon(True)
    thread_synchronize_data.start()
    Logger.info("start a new thread to synchronize data.")
except Exception as e:
    Logger.error("when start a new thread to synchronize_data!")
    Logger.error(repr(e))
    ToolFunctions.sys_exit(104)

# 交互逻辑
'''
新开一个线程  用于交互 即如何触发发送订单 管理订单池中的订单的状态 发送订单后收到回复之后 就可以将该订单 从订单池中pop
控制发送 继续任务 同样需要管理 继续任务的订单池 状态

'''
try:
    import InteractionLogic
    thread_dispatch_logic = threading.Thread(target = InteractionLogic.Work_Interaction_Loop,
                                             name = 'Interaction')
    thread_dispatch_logic.setDaemon(True)
    thread_dispatch_logic.start()
    Logger.info("start a new thread for interaction logic.")
except Exception as e:
    Logger.error("when start a new thread for interaction logic")
    Logger.fatal(repr(e))
    ToolFunctions.sys_exit(106)


import DataSynchronization
DataSynchronization.synchronize_data()
from GlobalContext import DispatchContext
for each_line_info in DispatchContext.lines:
    print(each_line_info)
    print(DispatchContext.lines_id_dict[each_line_info.order_id])


# main thread keeps waiting
while True:
    Logger.info("Main thread keeps alive.")
    disk_io_1 = psutil.disk_io_counters()
    disk_io_2 = psutil.disk_io_counters()
    disk_read_speed = disk_io_2.read_bytes - disk_io_1.read_bytes
    disk_write_speed = disk_io_2.write_bytes - disk_io_1.write_bytes
    Logger.info('CPU usage: ' + str(psutil.cpu_percent()) + '%;'
                 + ' Memory usage: ' + str(round(psutil.virtual_memory().used / 1000000, 2)) + ' MB, ' + str(psutil.virtual_memory().percent) + '%; '
                 + ' Disk IO: read = ' + str(round(disk_read_speed / 1000000, 2)) + 'MB/s, write = ' + str(round(disk_write_speed / 1000000, 2)) + 'MB/s')
    time.sleep(10)
# program end
