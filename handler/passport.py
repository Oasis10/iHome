# -*- coding:utf-8 -*-
import hashlib
import logging
from utils.session import Session
import re

import constants
from handler.bases import BaseHandler
from utils.response_code import RET
from utils.commons import required_login


class UserHandler(BaseHandler):
    """处理用户注册"""

    def put(self):
        """用户注册数据，存入数据库中"""
        # 从json中获取参数，手机号，密码，短信验证码
        mobile = self.json_data.get('mobile')
        password = self.json_data.get('password')
        sms_code = self.json_data.get('sms_code')

        # 判断传参情况
        if not all([mobile, password, sms_code]):
            resp = {
                'errno': RET.PARAMERR,
                'errmsg': '参数不完整'
            }
            return self.write(resp)

        # 判断手机号格式是否正确
        if not re.match(r'1[34578]\d{9}', mobile):
            resp = {
                'errno': RET.PARAMERR,
                'errmsg': '手机号格式不正确'
            }
            return self.write(resp)

        # 获取redis中的短信验证码
        try:
            exact_sms_code = self.redis.get('sms_code_%s'%mobile)
        except Exception, e:
            logging.error(e)
            resp = {
                'errno': RET.DBERR,
                'errmsg': '查询验证码失败'
            }
            return self.write(resp)

        # 判断redis中的验证码是否超过了有效期
        if exact_sms_code is None:
            resp = {
                'errno': RET.NODATA,
                'errmsg': '手机验证码已过期，请重试'
            }
            return self.write(resp)

        # 校验短信验证码
        if sms_code != exact_sms_code:
            resp = {
                'errno': RET.DATAERR,
                'errmsg': '手机验证码输入错误'
            }
            return self.write(resp)

        # 用户手机号及短信验证码校验通过，处理密码sha256
        encrypt_password = hashlib.sha256(password+constants.PASSWORD_SALT_KEY).hexdigest()

        # 将用户数据写入mysql数据库中
        sql = 'insert into ih_user_profile(up_name, up_mobile, up_passwd) VALUES(%(name)s, %(mobile)s ,%(passwd)s)'
        try:
            user_id = self.db.execute(sql, name=mobile, mobile=mobile, passwd=encrypt_password)
        except Exception, e:
            logging.error(e)
            resp = {
                'errno':RET.DBERR,
                'errmsg':'保存用户数据失败'
            }
            return self.write(resp)

        # 注册成功即认为用户已经登录
        try:
            session = Session(self)
            session.data['mobile'] = mobile
            session.data['name'] = mobile
            session.data['user_id'] = user_id
            session.data['avatar'] = constants.DEFAULT_AVATAR
            session.save()
        except Exception, e:
            logging.error(e)
            resp = {
                'errno':RET.SESSIONERR,
                'errmsg':'登录失败'
            }
            return self.write(resp)

        # 完成注册流程
        resp = {
            'errno': RET.OK,
            'errmsg': '注册成功'
        }
        self.write(resp)

    @required_login
    def get(self):
        """处理个人主页信息/头像内容"""
        # 第一种方法, 查询mysql数据库
        # user_id = self.session.data['user_id']
        # sql = 'select up_avatar from ih_user_profile WHERE up_user_id=%s;'
        # try:
        #     result = self.db.get(sql, user_id)
        # except Exception, e:
        #     logging.error(e)
        #     return self.write(dict(errno=RET.DBERR, errmsg='用户信息查询失败'))

        # 第二种方法,直接读取session数据
        name = self.session.data['name']
        mobile = self.session.data['mobile']
        avatar = self.session.data['avatar']
        return self.write(dict(
                        errno=RET.OK,
                        errmsg='ok',
                        data=dict(
                            name=name,
                            mobile=mobile,
                            avatar_url=constants.QINIU_URL_PREFIX+avatar
                        )))
        # return self.write(dict(errno=RET.OK, errmsg='系统默认头像',
        #                        avatar_url=constants.QINIU_URL_PREFIX+constants.DEFAULT_AVATAR))


    @required_login
    def post(self):
        """处理用户修改用户名"""
        user_id = self.session.data['user_id']
        name = self.get_argument('name')
        if name:
            sql = 'select up_user_id from ih_user_profile WHERE up_name=%s'
            try:
                result = self.db.get(sql, name)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='用户名查询失败'))
            # 名重复
            if result:
                return self.write(dict(errno=RET.DATAEXIST, errmsg='用户名已存在，请重新设置'))
            sql = 'update ih_user_profile set up_name=%(name)s WHERE up_user_id=%(user_id)s'
            try:
                self.db.execute(sql, name=name, user_id=user_id)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='用户名修改失败,请重试'))
            # 更新session中的name字段
            self.session.data['name'] = name
            # 保存到redis中
            try:
                self.session.save()
            except Exception, e:
                logging.error(e)
            # 用户名修改成功
            return self.write(dict(errno=RET.OK, errmsg='用户名修改成功!'))
        # 前端传输name字段失败
        return self.write(dict(errno=RET.PARAMERR, errmsg='修改失败,请重试'))


class SessionHandler(BaseHandler):
    """对于session资源的操作，包括登录登出"""

    def put(self):
        """登录"""
        # 从前端传输的json数据中取出手机号和密码信息
        mobile = self.json_data.get('mobile')
        password = self.json_data.get('password')

        # 首先判断是否参数是否完整
        if not all([mobile, password]):
            resp = {
                'errno':RET.PARAMERR,
                'errmsg':'参数不完整'
            }
            return self.write(resp)

        # 判断手机号是否合法
        if not re.match(r'1[34578]\d{9}$', mobile):
            print('------------判断是否进入了正则匹配手机号')
            return self.write(dict(errno=RET.DATAERR, errmsg='手机号输入有误'))

        # 从mysql数据库中取出密码
        sql = 'select up_user_id, up_name, up_passwd, up_avatar from ih_user_profile WHERE up_mobile = %(mobile)s'
        try:
            result = self.db.get(sql, mobile=mobile)
        except Exception, e:
            logging.error(e)
            resp = {
                'errno':RET.DBERR,
                'errmsg':'查询数据库信息失败'
            }
            return self.write(resp)

        # 判断是否有这个用户
        if not result:
            return self.write(dict(errno=RET.USERERR, errmsg='账号不存在,请重试!'))

        encypt_password = hashlib.sha256(password+constants.PASSWORD_SALT_KEY).hexdigest()

        #　校验用户输入的密码
        if encypt_password != result['up_passwd']:
            resp = {
                'errno':RET.LOGINERR,
                'errmsg':'手机号或密码错误，请重试'
            }
            return self.write(resp)

        # 用户密码输入正确，将用户信息写入session中
        try:
            session = Session(self)
            session.data['user_id'] = result['up_user_id']
            session.data['name'] = result['up_name']
            session.data['avatar'] = result['up_avatar'] if bool(result['up_avatar']) else constants.DEFAULT_AVATAR
            session.data['mobile'] = mobile
            session.save()
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.SESSIONERR, errmsg='登录失败'))
        return self.write(dict(errno=RET.OK, errmsg='OK'))


    @required_login
    def delete(self):
        """登出"""
        self.session.clear()
        return self.write(dict(errno=RET.OK, errmsg='OK'))

    def get(self):
        """判断用户登录状态"""
        data = self.get_current_user()
        user_name = data.get('name')
        if user_name:
            resp = {
             'errno':RET.OK,
             'errmsg':'ok',
             'data':{'name':user_name}
            }
            return self.write(resp)
        # 用户未登录
        return self.write(dict(errno=RET.NODATA))


class MobileAjaxHandler(BaseHandler):
    """处理检验手机号是否被注册过及是否合法ajax请求"""

    def get(self):

        mobile = self.get_argument('mobile')
        # 判断手机号格式是否正确
        if not re.match(r'1[34578]\d{9}', mobile):
            resp = {
                'errno': RET.PARAMERR,
                'errmsg': '手机号格式不正确'
            }
            return self.write(resp)

        sql = 'select up_user_id from ih_user_profile WHERE up_mobile=%s'
        try:
            result = self.db.get(sql, mobile)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg=''))
        if result:
            return self.write(dict(errno=RET.DATAEXIST, errmsg='号码已被注册'))
        return self.write(dict(errno=RET.OK, errmsg='该手机号码可用'))





