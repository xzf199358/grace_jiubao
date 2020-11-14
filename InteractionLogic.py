
from GlobalContext import *
from LoggerModule import Logger
import time
from ConfigManager import ConfigParameter

'''
思路：一个线程 实时从数据库读取订单数据 并生成订单列表 重复的id 不重复生成
交互线程 从订单列表中拿到订单 将之转发RCS 收到回复之后 将order_no 以及order_status_id 置掉
之后将 订单池中的 订单删除 完成一个完整的流程
优化项：  需要进入到RCS系统中  对订单的过程状态进行监控   输出不同状态的订单值
'''
def Work_Interaction_Loop():
    Logger.info('start interaction logic loop')
    from GlobalContext import DispatchContext
    # Logger.info('data_package_id : ' + str(DispatchContext.data_package_id))
    while True:
        DispatchContext.all_lock.acquire()
        try:
            for current_line in DispatchContext.lines:
                if current_line.messages is None:
                    current_line.send_generate_task_mesg()
                    Logger.info('send the request message !!!' + str(current_line.messages.request_message))
                print(current_line.messages)
                print(current_line)
                # print(DispatchContext.lines_id_dict[each_line_info.order_id])
        except Exception as e:
            Logger.error('when execute dispatch logic!')
            Logger.error(repr(e))

        DispatchContext.all_lock.release()
        Logger.info('Thread for interaction logic keeps alive.')
        time.sleep(0.3)  # sleep time unit is second

























