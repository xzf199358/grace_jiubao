#
import threading
import socket
from LoggerModule import Logger
from Line import *
from ToolFunctions import *


def open_listener():

    from GlobalContext import DispatchContext
    for each_line in DispatchContext.lines:
        # start a thread to listen line server
        ip_port = str(each_line.ip) + ':' + str(each_line.port)
        if ip_port in DispatchContext.address_list:
            continue
        DispatchContext.address_list.append(ip_port)
        thread_listener = threading.Thread(target=listen_a_port, args=(each_line.ip, each_line.port), name=('listener:' + ip_port))
        thread_listener.setDaemon(True)
        thread_listener.start()
        Logger.info("start a new thread for listener a port.")
    # listen query port
    for each_line in DispatchContext.lines:
        # start a thread to listen line server
        ip_port = str(each_line.query_ip) + ':' + str(each_line.query_port)
        if ip_port in DispatchContext.address_list:
            continue
        DispatchContext.address_list.append(ip_port)
        thread_listener = threading.Thread(target=listen_a_port, args=(each_line.query_ip, each_line.query_port), name=('listener:' + ip_port))
        thread_listener.setDaemon(True)
        thread_listener.start()
        Logger.info("start a new thread for listener a port to query.")
    return 0


def listen_a_port(this_ip, this_port):
    # connect
    from GlobalContext import DispatchContext
    ip_and_port = str(this_ip) + ':' + str(this_port)
    this_socket = do_connect(this_ip, this_port)

    while True:
        try:
            if this_socket is None:
                Logger.info('connect ' + str(ip_and_port) + ' error,try again!')
                this_socket = do_connect(this_ip, this_port)
                continue

            data = this_socket.recv(1024).decode('utf8')
            Logger.info('recv data package: ' + str(data))
            if is_heartbeat(data, this_socket):
                Logger.info('is_heartbeat ok')
                continue
            check_result = check_and_update_package_data(data)
            if check_result:
                Logger.info('add to line.messages')

            if data == '':  # 连接中断时返回''
                if ip_and_port in DispatchContext.ip_and_port_connect_dict.keys():
                    DispatchContext.ip_and_port_connect_dict[ip_and_port].close()
                    DispatchContext.ip_and_port_connect_dict.pop(ip_and_port)
                    Logger.info('pop socket:' + str(ip_and_port))
                this_socket = do_connect(this_ip, this_port)
                time.sleep(1)

        except Exception as e:
            Logger.error("when get data from tcp!")
            try:
                this_socket.send('HEAD00010006000000041234TAIL'.encode('utf8'))  # 发送心跳报文测试连接状态
            except:
                this_socket = do_connect(this_ip, int(this_port))
        time.sleep(0.1)


def is_heartbeat(data:str, this_socket):
    if data == 'HEAD00010006000000041234TAIL':
        this_socket.send('HEAD00010006000000044321TAIL'.encode('utf8'))
        return True
    return False


def do_connect(host,port):
    from GlobalContext import DispatchContext
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    # DispatchContext.all_lock.acquire()
    result = None
    try:
        str_address = str(host) + ':' + str(port)
        if str_address in DispatchContext.ip_and_port_connect_dict.keys():
            return DispatchContext.ip_and_port_connect_dict[str_address]

        Logger.info('start to connect this server:' + str_address)
        sock.connect((host, port))
        Logger.info('socket connect success!address: ' + str_address)
        DispatchContext.ip_and_port_connect_dict[str_address] = sock
        Logger.info('connect' + str_address + ' success')
        result = sock
    except Exception as e :
        Logger.info('tcp connect error,ip: ' + str(host) + ' ,port:' + str(port))
        # time.sleep(3)

    # DispatchContext.all_lock.release()
    return result


def check_and_update_package_data(package_data):
    package_data = package_data.strip()
    message_len = len(package_data)
    # print('the data length:' + str(len(package_data)))
    Logger.info('check_and_update_package_data this message')
    # if message_len != 28 or message_len != 40:
    #     Logger.info('package_data len error,ignore it!')
    #     return False
    # 交互响应
    if message_len == 28:
        if package_data[0:4] != 'HEAD' or package_data[24:28] != 'TAIL':
            Logger.info('package_data formal error,ignore it!')
            return False

        data_package_id = int(package_data[4:8])
        do_code = int(package_data[8:12])
        error_code = int(package_data[12:16])
        data_len = int(package_data[16:20])
        return_code = int(package_data[20:24])
        if do_code != 2 or error_code != 0:
            Logger.info('do_code or error_code error ignore it!')
            return False

        from GlobalContext import DispatchContext
        if data_package_id not in DispatchContext.package_id_line_dict.keys():
            Logger.info('have not send this package id')
            return False

        if return_code != 0:
            return False

        this_line: LineData = DispatchContext.package_id_line_dict[data_package_id]
        if this_line.messages is None:
            Logger.info('messages is None for check_and_update_package_data,line: ' + str(this_line))
            return False

        current_message = this_line.messages
        current_message.response_time = time.time()
        current_message.is_response = True
        current_message.response_message = package_data
        current_message.return_code = return_code
        Logger.info('add data to line!')
        return True
    # 查询回复
    if message_len == 40:
        if package_data[0:4] != 'HEAD' or package_data[36:40] != 'TAIL':
            Logger.info('package_data formal error,ignore it!')
            return False
        # print('data length is :'+str(message_len))
        '''将 数量 返回到 轨道类中  并更新到数据库'''
        data_package_id = int(package_data[4:8])
        opt_code = int(package_data[8:12])
        error_code = int(package_data[12:16])
        data_len = int(package_data[16:20])
        return_code = int(package_data[20:24])
        line_id = int(package_data[24:28])
        slice_num = int(package_data[28:32])
        real_basket_num = int(package_data[32:36])

        if opt_code != 3 or error_code != 0:
            Logger.info('do_code or error_code error ignore it!')
            return False

        from GlobalContext import DispatchContext
        if data_package_id not in DispatchContext.query_package_id_line_dict.keys():
            Logger.info('have not send this package id')
            return False

        this_line: LineData = DispatchContext.query_package_id_line_dict[data_package_id]
        if this_line.id == line_id:
            Logger.info('set line' + str(this_line.id) + '.basket_num = ' + str(real_basket_num) + ',slice_num = ' + str(slice_num))
            this_line.basket_num = real_basket_num
            this_line.slice_num = slice_num
        else:
            Logger.info('return line: ' + str(line_id) + '+basket num to line:' + str(this_line.id) + ', ignore it!')

        if this_line.query_messages is None:
            Logger.info('query_messages is None for check_and_update_package_data,line: ' + str(this_line))
            return False

        current_query_message = this_line.query_messages
        current_query_message.response_time = time.time()
        current_query_message.is_response = True
        current_query_message.response_message = package_data
        current_query_message.return_code = return_code

        return True






