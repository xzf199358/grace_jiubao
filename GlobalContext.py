# -*- coding: UTF-8 -*-
# This module is to store all the information that dispatch algorithms need

import threading
from Line import *


class DispatchContext:
    lines: List[OrderData] =[]
    lines_id_dict: Dict[int,OrderData] = {}   #存放 数据表订单 和 id
    lines_listindex_dict:Dict[int,OrderData] = {}  # 存放 line  的数组的索引
    db_connect = None
    package_id_line_dict: Dict[id, OrderData] = {}    # 发送的数据包和 订单之间的关系
    query_package_id_line_dict: Dict[id, OrderData] = {}
    data_package_id = 0
    address_list: List[str] = []

    all_lock = threading.Lock()


