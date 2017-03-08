#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: tomcat_deploy.py
@Create: 17/2/20 02:02
@Desc tomcat 发布页面
"""
from config import conf, code_info
from tomcat.tomcat_status import TomcatStatus
from util import tomcat_util as util, log_util


class TomcatDeploy(object):

    def __init__(self, tomcat_path, conf_path, host, heart_url):
        log_util.info("init deploy tomcat")
        self.tomcat_path = util.append_black_slash(tomcat_path)
        self.conf_path = util.append_black_slash(conf_path)
        self.heart_url = heart_url

        self.__request_timeout = 1
        self.__tomcat_war_dir_path = "%swebapps/" % self.tomcat_path
        self.__tomcatStatus = TomcatStatus(host, "Basic c2t5OGNoaTpjaGl0aWFueGlhbmc=")
        self.__run_pid = self.get_pid()

    def get_pid(self):
        return (util.run_cmd("cat %stomcat.pid" % self.tomcat_path)["info"][0]).replace("\n", "")

    def wait_for_deal_pre_resp(self):
        rst, cost = util.polling_check(self.__tomcatStatus.has_user_connect, conf.TOMCAT_STATUS__CHECK_CONNECT_TIMEOUT)
        log_util.info("wait_for_deal_pre_resp cost: %s s", cost)
        return rst

    def force_kill_pre(self):
        # pid_cmd = "ps -lfC java | grep [t]omcat | awk '{print $4}'"
        # pid = util.run_cmd(pid_cmd)["info"][0]
        # if pid == '':
        #     print "pid not exist"
        #     return
        log_util.info("try to kill pid: %s", self.__run_pid)
        if self.__run_pid != "":
            util.force_kill(int(self.__run_pid))

    def force_kill_current(self):
        self.__run_pid = self.get_pid()
        self.force_kill_pre()

    def check_run(self):
        if self.__run_pid != "":
            pid_cmd = "ps -p '%s' >/dev/null 2>&1; echo $?" % self.__run_pid
            result = util.run_cmd(pid_cmd)
            if result["code"] > 0 or result["info"][0].replace("\n", "") == "0":
                return True
        return False

    def __remove_unpack(self, wars_with_md5):
        for war_path in wars_with_md5.keys():
            war_name = util.get_file_name(war_path)
            war_pre_name = war_name[:-4]
            log_util.debug("start to remove war: %s", war_name)
            result = util.run_cmd("rm -rf %swebapps/%s" % (self.tomcat_path, war_name))
            if result["code"] > 0:
                log_util.error(result["info"][1])
                return False
            log_util.debug("start to remove war dir: %s", war_pre_name)
            result = util.run_cmd("rm -rf %swebapps/%s" % (self.tomcat_path, war_pre_name))
            if result["code"] > 0:
                log_util.error(result["info"][1])
                return False
        return True

    def __remove_work(self):
        log_util.debug("start to remove work dir")
        result = util.run_cmd("rm -rf %swork/Catalina" % self.tomcat_path)
        if result["code"] > 0:
            log_util.error(result["info"][1])
            return False
        return True

    def __copy_war(self, wars_with_md5):
        for war_path in wars_with_md5.keys():
            log_util.debug("start to copy war src [%s] to dst [%s]" % (war_path, self.__tomcat_war_dir_path))
            result = util.copy(war_path, self.__tomcat_war_dir_path)
            if result["code"] > 0:
                log_util.error(result["info"][1])
                return False
        return True

    def __copy_conf(self, conf_with_md5):
        for conf_path in conf_with_md5.keys():
            log_util.debug("start to copy conf src [%s] to dst [%s]" % (conf_path, self.conf_path))
            result = util.copy_not_del(conf_path, self.conf_path)
            if result["code"] > 0:
                log_util.error(result["info"][1])
                return False
        return True

    def __tomcat_wars_with_md5(self):
        return util.get_wars_with_md5(self.__tomcat_war_dir_path)

    def __tomcat_confs_with_md5(self):
        return util.get_confs_with_md5(self.conf_path)

    def check_md5(self, wars_with_md5, conf_with_md5):
        for war_path in wars_with_md5.keys():
            war_name = util.get_file_name(war_path)
            tomcat_wars_with_md5 = self.__tomcat_wars_with_md5()
            tomcat_war_path = self.__tomcat_war_dir_path + war_name
            log_util.debug("check war src [%s : %s] dst [%s : %s]"
                          % (war_path, wars_with_md5[war_path],
                             tomcat_war_path, tomcat_wars_with_md5[tomcat_war_path]))
            if wars_with_md5[war_path] != tomcat_wars_with_md5[tomcat_war_path]:
                return False

        for conf_path in conf_with_md5.keys():
            conf_name = util.get_file_name(conf_path)
            tomcat_confs_with_md5 = self.__tomcat_confs_with_md5()
            tomcat_conf_path = self.conf_path + conf_name
            log_util.debug("check conf src [%s : %s] dst [%s : %s]"
                          % (conf_path, conf_with_md5[conf_path],
                             tomcat_conf_path, tomcat_confs_with_md5[tomcat_conf_path]))
            if conf_with_md5[conf_path] != tomcat_confs_with_md5[tomcat_conf_path]:
                return False
        return True

    def __start_tomcat(self):
        result = util.run_cmd("/bin/sh %sbin/startup.sh" % self.tomcat_path)
        if result["code"] > 0:
            log_util.error("%s, %s" % (result["info"][0], result["info"][1]))
            return False
        return True

    def __is_tomcat_start(self):
        def __tomcat_not_start():
            return not util.is_request_200(self.heart_url, self.__request_timeout)
        rt, cost = util.polling_check(__tomcat_not_start, conf.TOMCAT__CHECK_START_TIMEOUT)
        log_util.info("check tomcat start cost: %s s" % cost)
        return rt

    def deploy(self, wars_with_md5, conf_with_md5):
        log_util.info("[start] deploy tomcat")

        log_util.info("[start] wait for deal pre resp")
        self.wait_for_deal_pre_resp()

        log_util.info("[start] force kill")
        self.force_kill_pre()

        log_util.info("[start] remove unpack")
        if not self.__remove_unpack(wars_with_md5):
            return code_info.REMOVE_UNPACK_FAIL

        log_util.info("[start] remove work")
        if not self.__remove_work():
            return code_info.REMOVE_WORK_FAIL

        log_util.info("[start] copy war")
        if not self.__copy_war(wars_with_md5):
            return code_info.COPY_WAR_FAIL

        log_util.info("[start] copy conf")
        if not self.__copy_conf(conf_with_md5):
            return code_info.COPY_CONF_FAIL

        log_util.info("[start] check md5")
        if not self.check_md5(wars_with_md5, conf_with_md5):
            return code_info.CHECK_FAIL

        log_util.info("[start] start tomcat")
        if not self.__start_tomcat():
            return code_info.START_SHELL_FAIL

        log_util.info("[start] start check deploy")
        if not self.__is_tomcat_start():
            return code_info.START_CHECK_FAIL

        log_util.info("[end] success")
        return code_info.SUCCESS

    def deploy_new(self, wars_with_md5, conf_with_md5):
        log_util.info("[start] deploy tomcat new")

        log_util.info("[start] remove unpack")
        if not self.__remove_unpack(wars_with_md5):
            return code_info.REMOVE_UNPACK_FAIL

        log_util.info("[start] remove work")
        if not self.__remove_work():
            return code_info.REMOVE_WORK_FAIL

        log_util.info("[start] copy war")
        if not self.__copy_war(wars_with_md5):
            return code_info.COPY_WAR_FAIL

        log_util.info("[start] copy conf")
        if not self.__copy_conf(conf_with_md5):
            return code_info.COPY_CONF_FAIL

        log_util.info("[start] check md5")
        if not self.check_md5(wars_with_md5, conf_with_md5):
            return code_info.CHECK_FAIL

        log_util.info("[start] start tomcat")
        if not self.__start_tomcat():
            return code_info.START_SHELL_FAIL

        log_util.info("[start] start check deploy")
        if not self.__is_tomcat_start():
            return code_info.START_CHECK_FAIL

        log_util.info("[end] success")
        return code_info.SUCCESS
if __name__ == '__main__':
    deployTom = TomcatDeploy("", "", "localhost:8080", "http://localhost:8080/index.html")
    deployTom.deploy(util.get_wars_with_md5("/data/test"), util.get_confs_with_md5("/data/test/conf"))[2]
