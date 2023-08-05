#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'James Iter'
__date__ = '16/1/17'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2015 by James Iter.'

import time
import os
import json
import thread
import signal


class KeepRead(object):
    """
    配置文件默认路径
        /etc/monitor_log.conf
        通过修改参数 KeepRead.config_path 来替换

    游标持久化默认存储路径
        /var/lib/misc/cursor.ml
        通过修改参数 KeepRead.cursor_path 来替换

    用法:
        设计过滤器方法,输入的参数仅有一个,即每次调用时所读取的行
        @staticmethod
        def filtrator(line=None):
            print line

        首先指定过滤器
        KeepRead.filtrator = filtrator
        启动
        KeepRead.launch()
    """
    # Example:
    # {"/var/log/messages": 2341, "/var/log/nginx/error_log": 3521}
    cursor = {}
    # Example:
    # [
    #   {"path": "/var/log/messages", "start_position": 0},
    #   {"path": "/var/log/nginx/error_log", "start_position": 0}
    # ]
    config = []
    config_path = '/etc/monitor_log.conf'
    cursor_path = '/var/lib/misc/cursor.ml'
    exit_flag = False
    thread_counter = 0
    filtrator = None

    def __init__(self):
        self.log_path = ''
        self.line = ''

    @classmethod
    def save_cursor(cls):
        dirname = os.path.dirname(cls.cursor_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(cls.cursor_path, 'w') as f:
            f.write(json.dumps(cls.cursor))

    @classmethod
    def restore_cursor(cls):
        if os.path.exists(cls.cursor_path):
            with open(cls.cursor_path) as f:
                cls.cursor = json.load(f)

    @classmethod
    def load_config(cls):
        if os.path.exists(cls.config_path):
            with open(cls.config_path, 'r') as f:
                cls.config = json.load(f)

    @classmethod
    def set_cursor(cls, log_path=None, offset=0):
        cls.cursor[log_path] = offset

    @classmethod
    def get_cursor(cls, log_path=None):
        return cls.cursor[log_path]

    @classmethod
    def increment_thread_counter(cls, number=1):
        cls.thread_counter += number

    @classmethod
    def get_exit_flag(cls):
        return cls.exit_flag

    def monitor(self):
        with open(self.log_path, 'rU') as f:
            self.increment_thread_counter(1)
            offset = self.get_cursor(log_path=self.log_path)
            if offset > 0:
                f.seek(offset)
            while True:
                if self.get_exit_flag():
                    self.increment_thread_counter(-1)
                    break

                self.line = f.readline()
                if self.get_cursor(log_path=self.log_path) == f.tell():
                    time.sleep(1)
                    continue

                self.set_cursor(log_path=self.log_path, offset=f.tell())
                self.dispose()

    def dispose(self):
        KeepRead.filtrator(self.line)

    @classmethod
    def signal_handle(cls, signum=0, frame=None):
        cls.exit_flag = True

    @staticmethod
    def launch():
        # ml for monitor log
        signal.signal(signal.SIGTERM, KeepRead.signal_handle)
        signal.signal(signal.SIGINT, KeepRead.signal_handle)
        KeepRead.load_config()
        KeepRead.restore_cursor()
        for item in KeepRead.config:
            kr = KeepRead()
            kr.log_path = item['path']

            if 'start_position' in item:
                KeepRead.cursor[kr.log_path] = item['start_position']
            elif kr.log_path not in KeepRead.cursor:
                KeepRead.cursor[kr.log_path] = 0

            thread.start_new_thread(kr.monitor, ())

        # 避免上面的for语句过快,导致线程还没有执行increment_thread_counter,
        # 就进入下面的while语句,这样thread_counter此时还为0,故而会跳过线程等待逻辑
        time.sleep(1)
        # 变通的方式实现线程等待目的
        while KeepRead.thread_counter > 0:
            time.sleep(1)
        KeepRead.save_cursor()
        print 'Bye-bye!'

