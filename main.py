#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: main.py
@Create: 17/2/23 09:12
@Desc logging 初始化
"""
import os
import sys
import time

from config import conf
from tomcat.tomcat_deploy import TomcatDeploy
from wrap.iptable_wrap import IptableWrap
from util import tomcat_util as util, log_util


def init():
    is_script_run, script_pid = get_script_info()
    if is_script_run and script_pid != "":
        raise Exception("script is running %s" % script_pid)
    set_script_pid()


def get_script_info():
    """
    :return: is_script_run, script_pid
    """
    if not os.path.exists(conf.SCRIPT__PID_FILE_PATH):
        return False, ""
    file_object = open(conf.SCRIPT__PID_FILE_PATH)
    try:
        pid = file_object.read()
    finally:
        file_object.close()

    pid_cmd = "ps -p '%s' >/dev/null 2>&1; echo $?" % pid
    result = util.run_cmd(pid_cmd)
    if result["code"] > 0:
        raise Exception("Check pid exist error: %s" % pid)
    if result["info"][0].replace("\n", "") == "0":
        return True, pid
    return False, pid


def set_script_pid():
    file_object = open(conf.SCRIPT__PID_FILE_PATH, 'w')
    try:
        file_object.write(str(os.getpid()))
    finally:
        file_object.close()


def single(wars_with_md5=util.get_wars_with_md5(conf.SRC_WAR_PATH),
           confs_with_md5=util.get_confs_with_md5(conf.SRC_CONF_PATH)):

    init()
    start = time.time()

    deploy_tom = TomcatDeploy(conf.TOMCAT1__PATH, conf.TOMCAT1__CONF_PATH, conf.TOMCAT1__HOST, conf.TOMCAT1__HEART_URL)
    result = deploy_tom.deploy(wars_with_md5, confs_with_md5)

    log_util.info("Final result: %s" % result[1])
    log_util.info("total cost: %s " % (time.time() - start))


def multi(cmd="start",
          wars_with_md5=util.get_wars_with_md5(conf.SRC_WAR_PATH),
          confs_with_md5=util.get_confs_with_md5(conf.SRC_CONF_PATH)):

    init()
    start = time.time()

    deploy_tom = TomcatDeploy(conf.TOMCAT1__PATH, conf.TOMCAT1__CONF_PATH, conf.TOMCAT1__HOST, conf.TOMCAT1__HEART_URL)
    deploy_tom2 = TomcatDeploy(conf.TOMCAT2__PATH, conf.TOMCAT2__CONF_PATH, conf.TOMCAT2__HOST, conf.TOMCAT2_HEART__URL)
    iptable_wrap = IptableWrap(deploy_tom, deploy_tom2)
    if cmd == "start":
        is_success, info = iptable_wrap.start_deploy(wars_with_md5, confs_with_md5)
    elif cmd == "chg":
        is_success, info = iptable_wrap.chg_iptable(wars_with_md5, confs_with_md5)
    else:
        is_success, info = (False, "Unknown cmd for: %s" % cmd)

    if not is_success:
        log_util.error(info)
    log_util.info("%s => total cost: %s" % (cmd, (time.time() - start)))
    return is_success, info


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "input: main.py [cmd(start, chg)]"
        exit(1)
    cmd_ = sys.argv[1]
    print "==cmd:" + cmd_
    try:
        is_success_, info_ = multi(cmd_)
    except Exception, e:
        is_success_, info_ = False, "Unknown error: %s" % e
    if not is_success_:
        print info_
        exit(1)
# single()
#multi()

