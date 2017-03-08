#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: tomcat_util.py
@Create: 17/3/7 16:44
@Desc tomcat 工具类
"""
from util import tomcat_util as util, log_util
import re


class IptableWrap(object):
    def __init__(self, tomcat_deploy, tomcat2_deploy):
        self.tomcat1 = tomcat_deploy
        self.tomcat2 = tomcat2_deploy
        pass

    @staticmethod
    def is_iptables_tom2():
        log_util.info("check iptables")
        result = util.run_cmd("iptables-save")
        iptables_info = result["info"][0]
        if result["code"] > 0:
            raise Exception("run iptables-save error")
        return re.search("-A PREROUTING -p tcp -m tcp --dport 8080 -j REDIRECT --to-ports 8180", iptables_info)

    def __run1(self):
        return self.tomcat1.check_run()

    def __run2(self):
        return self.tomcat2.check_run()

    def start_deploy(self, wars_with_md5, confs_with_md5):
        if IptableWrap.is_iptables_tom2():
            if self.__run1():
                log_util.info("tom1 is already running start to kill")
                self.tomcat1.force_kill_pre()
            if not self.__run1():
                code, info = self.tomcat1.deploy_new(wars_with_md5, confs_with_md5)
                if code > 0:
                    self.tomcat1.force_kill_current()
            else:
                code, info = (111, "kill tom1 fail")
        else:
            if self.__run2():
                log_util.info("tom2 is already running start to kill")
                self.tomcat2.force_kill_pre()
            if not self.__run2():
                code, info = self.tomcat2.deploy_new(wars_with_md5, confs_with_md5)
                if code > 0:
                    self.tomcat2.force_kill_current()
            else:
                code, info = (111, "kill tom2 fail")

        if code > 0:
            log_util.error("Deploy error: %s" % info)
            return False, info
        return True, "success"

    def chg_iptable(self, wars_with_md5, confs_with_md5):
        if not self.__run1() and not self.__run2():
            return False, "Nothing running cann't chg"
        if IptableWrap.is_iptables_tom2():
            if not self.__run1():
                return False, "current iptables is tom2, but tom1 is not running, cann't chg"

            if self.__run2():
                log_util.info("[start] kill tom8180")
                self.tomcat2.wait_for_deal_pre_resp()
                self.tomcat2.force_kill_pre()
            else:
                log_util.warn("Previous tomcat is not run，didn`t need kill")

            if self.tomcat1.check_md5(wars_with_md5, confs_with_md5):
                log_util.info("[start] chg iptable for tom8080")
                result = util.run_cmd("iptables -t nat -D PREROUTING -p tcp --dport 8080 -j REDIRECT --to-ports 8180")
                if result["code"] > 0:
                    return False, result["info"][1]
            else:
                return False, "check tom1's md5 fail, cann't chg"
        else:
            if not self.__run2():
                return False, "current iptables is tom1, but tom2 is not running, cann't chg"

            if self.__run1():
                log_util.info("[start] kill tom8080")
                self.tomcat1.wait_for_deal_pre_resp()
                self.tomcat1.force_kill_pre()
            else:
                log_util.warn("Previous tomcat is not run，didn`t need kill")

            if self.tomcat2.check_md5(wars_with_md5, confs_with_md5):
                log_util.info("[start] chg iptable for tom8180")
                result = util.run_cmd("iptables -t nat -A PREROUTING -p tcp --dport 8080 -j REDIRECT --to-ports 8180")
                if result["code"] > 0:
                    return False, result["info"][1]
            else:
                return False, "check tom2's md5 fail, cann't chg"

        return True, "success"
