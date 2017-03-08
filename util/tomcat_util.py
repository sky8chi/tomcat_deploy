#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
@Version: 1.0
@Author: sky8chi
@Contact: sky8chi@gmail.com
@Name: tomcat_util.py
@Create: 17/2/20 16:44
@Desc tomcat 工具类
"""
import hashlib
import os
import subprocess
import time
import urllib2
from util import log_util


def polling_check(func, timeout, check_sleep=1):
    """
    break condition
        func is return False
        or
        timeout
    """
    rt = False
    start_timestamp = time.time()
    # 检查是否还有外部链接
    for i in range(1, timeout):
        if not func():
            rt = True
            break
        if time.time() > (start_timestamp + timeout):
            break
        time.sleep(check_sleep)
    return rt, (time.time() - start_timestamp)


def force_kill(pid):
    try:
        os.kill(pid, 9)
        log_util.info('已杀死pid为%s的进程' % pid)
    except OSError, e:
        log_util.error("%s %s 没有如此进程!!!" % (OSError, e))


def run_cmd(cmd):
    y = subprocess.Popen(args=cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    return {"info": y.communicate(), "code": y.returncode}


def copy(src, des):
    cmd = "rsync -a --delete-after %s %s" % (src, des)
    return run_cmd(cmd)


def copy_not_del(src, des):
    cmd = "rsync -a %s %s" % (src, des)
    return run_cmd(cmd)


def is_request_200(url, timeout):
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req, timeout=timeout)
        response.close()
    except Exception, e:
        log_util.warn("%s,%s, 请求异常url: %s" % (Exception, e, url))
        return False
    if response.getcode() == 200:
        return True
    else:
        return False


def file_md5(filepath):
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
    f.close()
    return md5obj.hexdigest()


def get_wars_with_md5(root_dir):
    if not os.path.exists(root_dir):
        return {}
    wars_with_md5 = {}
    for file_ in os.listdir(root_dir):
        path = os.path.join(root_dir, file_)
        if os.path.isfile(path) and file_.endswith(".war"):
            wars_with_md5[path] = file_md5(path)
    return wars_with_md5


def get_confs_with_md5(root_dir):
    if not os.path.exists(root_dir):
        return {}
    conf_with_md5 = {}
    for file_ in os.listdir(root_dir):
        path = os.path.join(root_dir, file_)
        if os.path.isfile(path):
            conf_with_md5[path] = file_md5(path)
    return conf_with_md5


def get_file_name(file_path):
    return os.path.basename(file_path)


def is_file(file_path):
    return os.path.isfile(file_path)


def append_black_slash(path):
    if not path.endswith("/"):
        path += "/"
    return path
