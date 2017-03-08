#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: conf.py
@Create: 17/3/6 5:15
@Desc 配置文件
"""
import os
import logging
# =============== common ===============
WORK_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# =============== main =================
SCRIPT__PID_FILE_PATH = "%s/run.pid" % WORK_ROOT_PATH

# =============== log ==================
LOG__LEVEL = logging.INFO
LOG__USE_COLOR = True
LOG__FILE_PATH = '%s/../deploy.log' % WORK_ROOT_PATH

# =============== tomcat status page =======
TOMCAT_STATUS__CHECK_CONNECT_TIMEOUT = 10

# =============== src =================
SRC_WAR_PATH = "%s/../test" % WORK_ROOT_PATH
SRC_CONF_PATH = "%s/../test/conf" % WORK_ROOT_PATH

# =============== tomcat ===============
TOMCAT__CHECK_START_TIMEOUT = 200

TOMCAT1__PATH = "/data/install/tomcat/"
TOMCAT1__CONF_PATH = "/data/store/tomcatconf"
TOMCAT1__HOST = "127.0.0.1:8080"
TOMCAT1__HEART_URL = "http://%s/app/c.jsp" % TOMCAT1__HOST

TOMCAT2__PATH = "/data/install/tomcat2/"
TOMCAT2__CONF_PATH = "/data/store/tomcat2conf"
TOMCAT2__HOST = "127.0.0.1:8180"
TOMCAT2_HEART__URL = "http://%s/app/c.jsp" % TOMCAT2__HOST


