# -*- coding:utf-8 -*-


import json
import tornado.web
import logging
from utils.session import Session
from tornado.web import RequestHandler



class BaseHandler(RequestHandler):
    '''自定义基类，实现一些通用功能'''

    def prepare(self):
        '''预处理方法，只要用于处理前端传来的json数据'''
        # 判断传输的数据是否为json, 默认为空, 防止startswith方法异常
        if self.request.headers.get('Content-Type', '').startswith('application/json'):
            # 获取请求体数据
            req_json_data = self.request.body
            # 解析json数据成字典，并存储到对象中
            self.json_data = json.loads(req_json_data)
        else:
            # 设置默认值为空字典，防止异常
            self.json_data = {}

    def set_default_headers(self):
        # 设置默认响应头信息
        self.set_header('Content-Type', 'Application/json; charset=utf-8')

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def get_current_user(self):
        '''查询session数据'''
        self.session = Session(self)
        return self.session.data


class GetXsrfCookie(BaseHandler):
    def get(self):
        self.xsrf_token
        ip = self.request.remote_ip
        logging.info(ip+' : get xsrf cookie success!')
        self.write('get xsrf cookie success!')

class StaticHandler(tornado.web.StaticFileHandler):
    '''重写静态页面处理类，初始化即获取xsrf_token'''
    def __init__(self, *args, **kwargs):
        super(StaticHandler, self).__init__(*args, **kwargs)
        # 获取xsrf_token
        self.xsrf_token
