#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: tomcat_status.py
@Create: 17/2/17 15:11
@Desc: tomcat status 页面
"""
import re
import urllib2
from bs4 import BeautifulSoup
from util import log_util


class TomcatStatus(object):
    def __init__(self, host, auth):
        self.host = host
        self.auth = auth
        self.__url = ''.join(["http://", host, "/manager/status"])
        self.__self_verify_request = "GET /manager/status HTTP/1.1"
        self.__request_timeout = 1
    
    def __request_url(self):
        req = urllib2.Request(self.__url)
        req.add_header("Authorization", self.auth)
        response = urllib2.urlopen(req, timeout=self.__request_timeout)
        self.__body = response.read()
        response.close()
    
    def has_user_connect(self):
        try:
            self.__request_url()
        except Exception, e:
            log_util.error("%s : %s" % (Exception, e))
            return True
        has_connect = False

        # 因页面table会发生变化，固用正则先抓取大概范围
        # soup = BeautifulSoup(self.__body, "html.parser")
        # tables = soup.findAll('table')
        # status_table = tables[-2]

        http_info = re.search(r"(<h1>http-\d+</h1>[\s\S]*?</table>)", self.__body).group(1)
        soup = BeautifulSoup(http_info, "html.parser")
        tables = soup.findAll('table')
        status_table = tables[0]

        trs = status_table.findAll("tr")
        trs_len = len(trs)
        for (idx, th) in enumerate(trs[0].findAll("th")):
            th_txt = th.getText()
            if th_txt == "Stage":
                stage_idx = idx
            elif th_txt == "Request":
                request_idx = idx
            log_util.debug("connect[ stage: %s, request: %s ]" % (idx, th.getText()))

        log_util.debug("stageIdx: %s, requestIdx: %s, trsLen: %s" % (stage_idx, request_idx, trs_len))
        for tr in trs[1:trs_len]:
            tds = tr.findAll("td")
            stage = tds[stage_idx].getText()
            request = tds[request_idx].getText()
            log_util.debug("current connects [ stage: %s, request: %s ]" % (stage, request))
            if (stage == "K" or request != "?") and request != self.__self_verify_request:
                log_util.info("Some url is connected: stage[%s], request[%s]" % (stage, request))
                has_connect = True
                break
        return has_connect
if __name__ == '__main__':
    tom = TomcatStatus("192.168.78.111:8180", "Basic c2t5OGNoaTpjaGl0aWFueGlhbmc=")
    # tom = TomcatStatus("localhost:8080", "Basic dG9tY2F0OnMzY3JldA==")
    print tom.has_user_connect()

