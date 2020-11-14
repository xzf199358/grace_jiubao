# -*- coding: UTF-8 -*-
# database interface functions

from LoggerModule import Logger


def execute_commit_sql(database_connection, sql_sentence):
    rows = None
    error_info = None
    try:
        cur = database_connection.cursor()
        cur.execute(sql_sentence)
        rows = cur.fetchall()
        database_connection.commit()
        cur.close()
        # Logger.debug('One SQL was successfully executed: \n' + sql_sentence)

    except Exception as e:
        Logger.error('One SQL failed to execute: \n' + str(sql_sentence))  # need use str() conversion to avoid sql_sentence is None
        error_info = 'Error: ' + str(repr(e))
        Logger.error(error_info)

    return rows, error_info


def test_database_connection(database_connection):
    rows, error_info = execute_commit_sql(database_connection, "select 1;")
    if error_info is not None or rows is None or len(rows) <= 0:
        return False  # connection is bad
    else:
        return True  # connection is good


