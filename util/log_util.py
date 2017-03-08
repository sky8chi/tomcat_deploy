#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: log_util.py
@Create: 17/2/22 16:02
@Desc logging 初始化
"""
import logging
import sys
from config import conf

__all__ = ['debug', 'info', 'warn', 'error', 'critical', 'exception']
logger = None


def init():
    global logger
    if logger is None:
        logger = logging.getLogger()
        if conf.LOG__USE_COLOR:
            add_color_handler()
        else:
            add_def_handler()

        cur_mod = sys.modules[__name__]
        log_func_names = ['debug', 'info', 'warn', 'error', 'critical', 'exception']
        for func_name in log_func_names:
            func = getattr(logger, func_name)
            setattr(cur_mod, func_name, func)


def add_def_handler():
    logging.basicConfig(level=conf.LOG__LEVEL,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        # datefmt='%a, %d %b %Y %H:%M:%S', # Thu, 23 Feb 2017 09:32:25
                        datefmt='%b %d %H:%M:%S',
                        filename=conf.LOG__FILE_PATH,
                        filemode='a')


def add_color_handler():
    global logger
    handler = logging.FileHandler(conf.LOG__FILE_PATH, "a")
    handler.setFormatter(ColorFormatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                        datefmt='%b %d %H:%M:%S'))
    logger.root.setLevel(conf.LOG__LEVEL)
    logger.addHandler(handler)


class ColorFormatter(logging.Formatter):

    COLOR_RED = '\033[1;31m'
    COLOR_GREEN = '\033[1;32m'
    COLOR_YELLOW = '\033[1;33m'
    COLOR_BLUE = '\033[1;34m'
    COLOR_PURPLE = '\033[1;35m'
    COLOR_CYAN = '\033[1;36m'
    COLOR_GRAY = '\033[1;37m'
    COLOR_WHITE = '\033[1;38m'
    COLOR_RESET = '\033[1;0m'

    LOG_COLORS = {
        'DEBUG': '%s',
        'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
        'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
        'ERROR': COLOR_RED + '%s' + COLOR_RESET,
        'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
        'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
    }

    def __init__(self, fmt, datefmt):
        super(ColorFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        level_name = record.levelname
        msg = super(ColorFormatter, self).format(record)
        return self.LOG_COLORS.get(level_name, "%s") % msg

init()

