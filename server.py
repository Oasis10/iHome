# -*- coding:utf-8 -*-

import tornado.options
import tornado.ioloop
import tornado.web
import torndb
import redis
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from urls import urls
import config

define('port', default=8000, type=int, help='run server on defined port')

class Application(tornado.web.Application):
    '''继承自tornado.web.Application，重写以添加数据库连接'''

    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法，形成完整的app对象
        super(Application, self).__init__(*args, **kwargs)
        # mysql连接对象
        self.db = torndb.Connection(**config.mysql_options)
        # redis连接对象 默认localhost 6379
        self.redis = redis.StrictRedis()

def main():
    # 设置日志保存目录
    options.log_file_prefix = config.log_file_path
    # 设置log等级
    options.logging = config.log_level
    # 解析命令行
    tornado.options.parse_command_line()
    # 创建应用
    app = Application(urls, **config.settings)
    # 启动服务器
    http_server = HTTPServer(app)
    # 监听
    http_server.listen(options.port)
    # 启动ioloop
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
