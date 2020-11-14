
from typing import Dict, List, Set
from enum import Enum
import DatabaseInterface
from LoggerModule import Logger
from SqlCollection import SqlCollection
import socket
import time
from DatabaseConnectionPool import DatabaseConnectionPool as db_pool
import json
import requests

class LineDataType(Enum):
    put_line = 1
    fetch_line = 2  # 设备出料，agv取料


'''  发送订单 到 HTTP 服务器 的消息类  主要用于生成 发送消息 管理消息模板'''
class OrderMessage:
    def __init__(self):
        self.data_package_id: int = None
        self.reqCode = None
        self.taskType = None
        self.positionCode1 = None
        self.positionCode2 = None
        self.request_message = None
        self.request_times: int = 0
        self.request_time = None
        self.response_time = None
        self.response_message:json = None
        self.is_response = False
        self.return_code:int = -1


''' 订单类 用于管理 从数据库中读取上来的订单数据  并初始化成 
在数据库读取之后 需要初始化成订单对象 并且 载入到订单列表中 也叫订单池 两个函数可以发送 任务消息  以及继续任务消息 
'''
class OrderData:
    def __init__(self):
        self.order_id:int = None
        self.order_type_id:int = None
        self.order_status_id:int = None
        self.location_id: int = None
        self.location_name = None
        self.destination_location_id:int = None
        self.destination_location_name = None
        self.priority:int = None
        self.is_sent:bool = None
        self.messages: OrderMessage = None    #
        self.continue_tak_messages: OrderMessage = None
        self.sent_back_database_times:int = 0

    def __str__(self):

        _order_id = ''
        if self.order_id is not None:
            _order_id = str(self.order_id)

        _order_type_id = ''
        if self.order_type_id is not None:
            _order_type_id = str(self.order_type_id)

        _order_status_id = ''
        if self.order_status_id is not None:
            _order_status_id = str(self.order_status_id)

        _location_id = ''
        if self.location_id is not None:
            _location_id = str(self.location_id)

        _location_name = ''
        if self.location_name is not None:
            _location_name = str(self.location_name)

        _destination_location_id = ''
        if self.destination_location_id is not None:
            _destination_location_id = str(self.destination_location_id)

        _destination_location_name = ''
        if self.destination_location_name is not None:
            _destination_location_name = str(self.destination_location_name)

        _priority = ''
        if self.priority is not None:
            _priority = str(self.priority)

        _is_sent = ''
        if self.is_sent is not None:
            _is_sent = str(self.is_sent)

        return ('OrderData: Order_id=' + _order_id
                + ' ,order_type_id=' + _order_type_id
                + ' ,order_status_id =' + _order_status_id
                + ' ,location_id=' + _location_id
                + ' ,location_name=' + _location_name
                + ' ,destination_location_id=' + _destination_location_id
                + ' ,destination_location_name=' + _destination_location_name
                + ' ,priority=' + _priority
                + ',is_sent = ' +_is_sent
                )

    def send_generate_task_mesg(self):
        ''' 发送 任务方法 '''
        from GlobalContext import DispatchContext
        # if self.is_sent is False:
        #     Logger.info('this line.message has not sent!,try to  send message!')
        #     return -1
        if self.messages is None:
            new_message = OrderMessage()
            new_message.data_package_id = get_data_package_id()
            temp_message = {"reqCode": "2312257536",
                            "taskTyp": "W01",
                            "wbCode": "",
                            "positionCodePath": [{"positionCode": "A2", "type": "00"},
                                                 {"positionCode": "A4", "type": "00"}],
                            "podCode": "-1",
                            "AgvCode": "6"}
            #选择发送订单的模板   # 1 : W01  2：W02  数据库插入时 需要控制 订单类型 即模板类型
            if self.order_type_id == 1:
                # 1 : W01  2：W02
                temp_message['taskTyp'] = 'W01'
            else:
                # 1 : W01  2：W02
                temp_message['taskTyp'] = 'W02'

            temp_message["reqCode"] = str(new_message.data_package_id)
            temp_message['positionCodePath'][0]['positionCode'] = str(self.location_name)
            temp_message['positionCodePath'][1]['positionCode'] = str(self.destination_location_name)
            new_message.request_message = json.dumps(temp_message)

            try:
                url = "http://192.168.101.34:80/cms/services/rest/hikRpcService/genAgvSchedulingTask"
                a = requests.post(url)
                headers = {'content-type': 'application/json'}
                ret = requests.post(url, data=new_message.request_message, headers=headers)
                new_message.request_times = 1
                new_message.request_time = time.time()
                self.is_sent = True
                Logger.info('this line has sent the request for generating  task!!')
                print(ret.status_code)
                if ret.status_code == 200:
                    Logger.info(' this line message has been responed, send status:200!')
                    text = json.loads(ret.text)
                    Logger.info('recv the return message ' + str(text))
                    new_message.is_response = True         # 发送已收到回复
                    new_message.response_message = text    # 记录发送之后，收到的回复的数据
                    new_message.return_code = 0            # 发送已收到回复
                else:
                    Logger.info(' the status_code is not 200  some error occur! please check it now' + str(ret.status_code))
                self.messages = new_message
                DispatchContext.package_id_line_dict[new_message.data_package_id] = self
            except Exception as e:
                Logger.error('the socket connect failed!')
                Logger.error(repr(e))
        else:
            '''
            消息 不为空  表示已经发送了 消息
            '''
            if self.messages.is_response:  # 消息发送已经收到回复
                Logger.info('this request message is responsed,need not to send message again!')
            else:  # when return != 0 发送了没有收到回复  需要再次发送
                self.messages.request_times += 1
                self.messages.request_time = time.time()
                url = "http://192.168.101.34:80/cms/services/rest/hikRpcService/genAgvSchedulingTask"
                a = requests.post(url)
                headers = {'content-type': 'application/json'}
                ret = requests.post(url, data = self.messages.request_message, headers=headers)
                print(ret.status_code)
                if ret.status_code == 200:
                    text = json.loads(ret.text)
                    Logger.info('recv the return message ' + str(text))
                    self.messages.response_message = text
                    self.messages.return_code = 0
                Logger.info('message is not responsed,send again:' + str(self.messages.request_message))
        return 0
    def send_continue_task_mesg(self):
        '''  发送 继续任务 '''
        pass



#从数据库载入订单数据
def get_order_info(database_connection):
    db_conn = database_connection
    sql_sentence = SqlCollection.get_order_info
    rows, error_info = DatabaseInterface.execute_commit_sql(db_conn, sql_sentence)
    if error_info is not None or rows is None:
        Logger.error("get agv info failed due to SQL execution! error_info: " + str(error_info))
        return None
    else:
        return rows


def load_order_info(rows) -> int:
    if rows is None:
        Logger.error('input row is None!')
        return -1
    line_count = len(rows)
    if line_count <= 0:
        Logger.info("no line info to load.")
        return 0
    for each_line in range(0, line_count):
        current_row = rows[each_line]
        order_line_info = resolve_line_info(current_row)

        if order_line_info is None:
            Logger.error('orderdata ignored  row = ' + str(current_row))
            continue
        # if line_info.ip is None or line_info.port is None or line_info.type_id is None:
        #     Logger.error('linedata ignored2. row = ' + str(current_row))
        #     continue
        from GlobalContext import DispatchContext
        if order_line_info.order_id not in DispatchContext.lines_id_dict.keys():
            DispatchContext.lines.append(order_line_info)
            DispatchContext.lines_listindex_dict[DispatchContext.lines.index(order_line_info)] = order_line_info
            DispatchContext.lines_id_dict[order_line_info.order_id] = order_line_info
    return 0


#解析数据库读取上来的数据 并初始化成 单个的订单对象
def resolve_line_info(current_row) -> OrderData or None:
    if current_row is None:
        Logger.error('input current_row is None for resolve_line_info!')
        return None
    try:  # 数据解析
        order_line_info = OrderData()
        order_line_info.order_id = int(current_row[0])

        if current_row[1] is not None:
            order_line_info.order_type_id = int(current_row[1])
        else:
            order_line_info.order_type_id = None

        if current_row[2] is not None:
            order_line_info.order_status_id = int(current_row[2])
        else:
            order_line_info.order_status_id = None

        if current_row[3] is not None:
            order_line_info.location_id = str(current_row[3])
        else:
            order_line_info.location_id = None

        if current_row[4] is not None:
            order_line_info.location_name =current_row[4]
        else:
            order_line_info.location_name = None

        if current_row[5] is not None:
            order_line_info.destination_location_id = int(current_row[5])
        else:
            order_line_info.destination_location_id = 0

        if current_row[6] is not None:
            order_line_info.destination_location_name = current_row[6]
        else:
            order_line_info.destination_location_name = None

        if current_row[7] is not None:
            order_line_info.priority = int(current_row[7])
        else:
            order_line_info.priority = 0

        order_line_info.is_sent = False

        return order_line_info
    except Exception as e:
        Logger.error("cannot resolve loaded line_info: " + str(current_row))
        Logger.error(repr(e))
        return None



# 实时更新订单状态 订单编号 到 数据库 对应的 order id 中
def send_order_status_to_database(order_no_value,order_status_value,order_id):
    Logger.info('try to update order line ,id:' + str(order_id) + ' ,order_no :' + str(order_no_value) +',order_status :'+str(order_status_value))
    if order_id is None:
        Logger.info('order_id is None for send_order_status_to_database!')
        return -1
    if order_no_value is None:
        Logger.info('order_no_value is None for send_order_status_to_database!')
        return -2
    if order_status_value is None:
        Logger.info('order_status_value is None for send_order_status_to_database!')
        return -3

    sql_sentence = SqlCollection.update_order_info.format(
        order_no =r"'" + str(order_no_value) + r"'",
        order_status_id = order_status_value,
        id = order_id
    )
    from GlobalContext import DispatchContext
    rows, error_info = DatabaseInterface.execute_commit_sql(DispatchContext.db_connect, sql_sentence)
    if error_info is not None or rows is None:
        Logger.error('send_order_status_to_database error!!! error_info: ' + str(error_info))
        return -2
    return 0


def update_order_status_to_database()->int:
    from GlobalContext import DispatchContext
    for this_line in DispatchContext.lines:
        if this_line.messages is None:
            Logger.info('this_line  message is not responed !')
            continue
        else:
            if this_line.messages.request_message is not None and this_line.messages.is_response is True:
                ''' 临时方案 需要将返回来的数据中获取订单编号订单状态 目前暂定 4 ,即接收到回复之后将订单置为4'''
                temp_order_num = str(this_line.messages.response_message['data'])
                temp_order_status = 4
                send_result = send_order_status_to_database(temp_order_num,temp_order_status,this_line.order_id)
                this_line.sent_back_database_times += 1
                if send_result < 0:
                    Logger.info('send io basket_num to database  failed !!!')
            else:
                Logger.info(' this line message is not responsed!')

        if this_line.sent_back_database_times >= 3:
            # 内存回收
            temp_order_id = this_line.order_id
            DispatchContext.lines_listindex_dict.pop(int(DispatchContext.lines.index(this_line)))
            DispatchContext.lines_id_dict.pop(int(this_line.order_id))
            DispatchContext.lines.remove(this_line)
            Logger.info('line has been removed from DispatchContext.lines for order_id :' + str(temp_order_id))
    return 0




#生成包数据 即重复 req_code
def get_data_package_id() -> int:
    from GlobalContext import DispatchContext
    DispatchContext.data_package_id = (DispatchContext.data_package_id + 1) % 10000
    for each_line in DispatchContext.lines:
        if each_line.messages is not None:
            temp_id = each_line.messages.data_package_id
            if temp_id is not None and DispatchContext.data_package_id == temp_id:
                DispatchContext.data_package_id = (DispatchContext.data_package_id + 1) % 10000
                print(DispatchContext.data_package_id)
    return DispatchContext.data_package_id









