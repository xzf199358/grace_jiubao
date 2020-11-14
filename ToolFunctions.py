# -*- coding: UTF-8 -*-
# This module is to share some useful functions

import sys
import queue
from enum import Enum
import threading
from typing import TypeVar, Iterable, Tuple, Dict, List, Set


def sys_exit(exit_code, wait_time = 60):
    print('Program is exiting in ' + str(wait_time) + ' seconds...')
    print('Or press any key to exit now: ')
    thread_sys_exit_get_input = threading.Thread(target = input, name = 'thread_sys_exit_get_input')
    thread_sys_exit_get_input.setDaemon(True)
    thread_sys_exit_get_input.start()
    thread_sys_exit_get_input.join(wait_time)
    sys.exit(exit_code)


# sys_exit(1, 5)

