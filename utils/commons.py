# -*- coding:utf-8 -*-

import functools
from utils.response_code import RET

def required_login(function):

    @functools.wraps(function)
    def wrapper(request_handler, *args, **kwargs):

        if not request_handler.get_current_user():
            # 用户未登录
            resp = {
                'errno':RET.SESSIONERR,
                'errmsg':'用户未登录'
            }
            request_handler.write(resp)
        else:
            print '用户已经登录'
            function(request_handler, *args, **kwargs)
    return wrapper