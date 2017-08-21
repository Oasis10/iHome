# -*- coding:utf-8 -*-

import os
import constants

# 配置参数
settings = dict(
    debug=True,
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    # xsrf_cookies=True,
    xsrf_cookies=False,
    cookie_secret=constants.XSRF_TOKEN
)

# mysql配置
mysql_options = dict(
    host='localhost',
    database='ihome',
    user='root',
    password='mysql'
)

# log日志存放目录
log_file_path = './logs/log'
# log等级
log_level = 'debug'