# -*- coding:utf-8 -*-

import uuid
import json
import constants
import logging


class Session(object):
    '''session类'''

    def __init__(self, request_handler_obj):

        # 获取cookie
        self.request_handler_obj = request_handler_obj
        session_id = request_handler_obj.get_secure_cookie('session_id')
        # 进行判断用户是否为第一次访问网站
        if session_id is None:
            # 用户第一次访问，创建session，生成uuid
            self.sid = uuid.uuid4().get_hex()
            # 预留一个容器，保存用户数据
            self.data = {}
        else:
            # 用户不是第一次访问
            self.sid = session_id
            try:
                json_str_data = self.request_handler_obj.redis.get('session_%s'%self.sid)
            except Exception, e:
                logging.error(e)
                raise e

            # 如果恰好session过期
            if json_str_data is None:
                self.data = {}
            else:
                self.data = json.loads(json_str_data)


    def save(self):
        '''将session数据保存到redis中'''
        # 将self.data数据转为json格式
        json_str_data = json.dumps(self.data)
        try:
            self.request_handler_obj.redis.setex('session_%s'%self.sid,
                                                 constants.SESSION_EXPIRE_TIME, json_str_data)
        except Exception, e:
            logging.error(e)
            raise e
        else:
            # 将self.sid设置到用户cookie当中去
            self.request_handler_obj.set_secure_cookie('session_id', self.sid)

    def clear(self):
        '''删除session数据'''
        # 删除redis数据库中的session数据
        try:
            self.request_handler_obj.redis.delete('session_%s'%self.sid)
        except Exception, e:
            logging.error(e)
        # 删除用户cookie数据
        self.request_handler_obj.clear_cookie('session_id')



