# -*- coding: UTF-8 -*-

from DatabaseConnectionPool import DatabaseConnectionPool as db_pool
from LoggerModule import Logger
import DatabaseInterface
from Line import *
from GlobalContext import DispatchContext
import time


class DatabaseResource:
    database_connection = None

def load_data():
    if DatabaseResource.database_connection is None:
        DatabaseResource.database_connection = db_pool.get_connection()
    db_conn = DatabaseResource.database_connection

    lines = get_order_info(db_conn)
    load_result = load_order_info(lines)
    if load_result < 0:
        return -1

    return 0





def synchronize_data():
    if DatabaseResource.database_connection is None or DispatchContext.db_connect:
        DatabaseResource.database_connection = db_pool.get_connection()
    db_conn = DatabaseResource.database_connection
    DispatchContext.db_connect = db_conn
    Logger.info('Starting to synchronize data with database in this cycle...')
    while True:
        try:
            error_flag = False
            Logger.info('Starting to synchronize data with database in this cycle...')
            # synchronizing data

            # data_package_id

            # write config_file_path to config.ini
            import configparser
            import os
            config_file_path = os.getcwd() + "/config/config.ini"
            config_writer = configparser.ConfigParser()
            config_writer.read(config_file_path)
            config_writer.set('tcp_connect_config', 'data_package_id', str(DispatchContext.data_package_id))
            config_writer.write(open(config_file_path, 'w'))

            try:
                DispatchContext.all_lock.acquire()

                # 实时 将数据库中的数据 读取到内存中
                lines = get_order_info(db_conn)
                load_result = load_order_info(lines)
                if load_result < 0:
                    Logger.error('send_database_agv_command failed!')
                    error_flag = True

                # 实时将 订单返回的数据  回写到数据库
                update_result = update_order_status_to_database()
                if update_result < 0:
                    Logger.error('send_database to  order_info order_status failed!')
                    error_flag = True

                # update_result = refresh_line_io_states(db_conn)
                # if update_result < 0:
                #     Logger.error('send_database_agv_command failed!')
                #     error_flag = True

                # update_result = update_line_status_to_database()
                # if update_result < 0:
                #     print(update_result)this_line basket num for update_all_io_to_zero!
                #     Logger.error('send_database line status  to io_state failed!')
                #     error_flag = True

            except Exception as e:
                Logger.error('when refresh data to DispatchContext!')
                Logger.error(repr(e))

            DispatchContext.all_lock.release()
            if error_flag:
                raise Exception('error happened when synchronize data!')

            # from GlobalContext import DispatchContext
            for each_line_info in DispatchContext.lines:
                print(each_line_info)
                print(DispatchContext.lines_id_dict[each_line_info.order_id])

            # from Line import send_order_status_to_database
            # send_order_status_to_database('erghyfjugkyf',4,2)

        except Exception as e:
            Logger.error("when synchronizing data with database!")
            Logger.error(repr(e))

            # test database connection
            test_db_result = DatabaseInterface.test_database_connection(db_conn)
            if test_db_result:
                Logger.info('database connection for synchronization data was tested and showed to be good.')
            else:
                # connection is bad, try to close current connection and get a new one
                Logger.error("synchronize_data(): database connection is bad, trying to close current connection and get a new one.")
                old_db_conn = db_conn
                new_db_conn = db_pool.get_connection()
                if new_db_conn is None:
                    Logger.error("synchronize_data(): cannot get a new database connection!")
                else:
                    Logger.info("synchronize_data(): already got a new database connection.")
                    db_conn = DatabaseResource.database_connection = new_db_conn
                    try:
                        old_db_conn.close()
                    except Exception as e2:
                        Logger.error('synchronize_data():  when try to close the old database connection after getting a new one!')
                        Logger.error(repr(e2))

        Logger.info('Thread for data synchronization keeps alive.')
        time.sleep(0.3)  # sleep time unit is second


