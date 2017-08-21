# -*- coding:utf-8 -*-

import random
import bases
import constants
import logging
import re
from utils.captcha.captcha import captcha
from utils.response_code import RET
from lib.yuntongxun.send_sms import ccp

class ImageCodeHandler(bases.BaseHandler):
    '''图片验证码处理类'''

    def get(self):
        '''获取图片验证码'''
        image_code_id = self.get_argument('id')
        # 生成图片验证码
        name, text, image = captcha.generate_captcha()
        try:
            self.redis.setex('image_code_%s'%image_code_id, constants.IMAGE_CODE_EXPIRE_TIME, text)
        except Exception, e:
            logging.error(e)
            # self.send_error(500)
            info = {'errno':RET.DBERR, 'errmsg':'保存数据失败'}
            self.write(info)
        else:
            self.set_header('Content-Type', 'image/jpg')
            self.write(image)


class SMSCodeHandler(bases.BaseHandler):
    '''短信验证码处理类'''
    def get(self):
        '''获取短信验证码'''
        # 需要的参数：手机号，图片验证码，图片验证码编号
        mobile = self.get_argument('mobile')
        image_code_text = self.get_argument('image_code_text')
        image_code_id = self.get_argument('image_code_id')

        # 判断手机号是否合法
        if not re.match('1[34578]\d{9}', mobile):
            # 匹配手机号失败，返回错误信息
            resp = {
                'errno': RET.PARAMERR,
                'errmsg': '手机号码格式不正确'
            }
            return self.write(resp)

        # 再次确认手机号是否注册过
        sql = 'select up_user_id from ih_user_profile WHERE up_mobile=%s'
        try:
            result = self.db.get(sql, mobile)
        except Exception, e:
            logging.error(e)
        if result:
            return self.write(dict(errno=RET.DATAEXIST, errmsg='号码已被注册，请更换号码后重试'))

        # 判断图片验证码
        try:
            exact_image_code = self.redis.get('image_code_%s'%image_code_id)
        except Exception, e:
            logging.error(e)
            resp = {
                'errno': RET.DBERR,
                'errmsg': '保存图片验证码失败'
            }
            return self.write(resp)

        if exact_image_code is None:
            resp = {
                'errno':RET.NODATA,
                'errmsg':'图片验证码已过期，请刷新重试！'
            }
            return self.write(resp)

        # 判断用户输入的图片验证码是否正确
        if image_code_text.lower() != exact_image_code.lower():
            resp = {
                'errno':RET.DATAERR,
                'errmsg':'图片验证码输入有误',
            }
            return self.write(resp)

        # 图片验证码校验通过，删除redis中的图片验证码
        try:
            self.redis.delete('image_code_%s'%image_code_id)
        except Exception, e:
            logging.error(e)

        # 生成手机验证码, 格式为六位数字
        sms_code = '%06d'%random.randint(0, 999999)
        # 将短信验证码存入redis数据库中
        try:
            self.redis.setex('sms_code_%s'%mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
        except Exception, e:
            logging.error(e)
            resp = {
                'errno':RET.DBERR,
                'errmsg':'保存手机验证码失败'
            }
            return self.write(resp)

        # 借助云通讯，让云通讯发送短信给用户
        # try:
        #     ccp.send_templates_sms(mobile, [sms_code, str(constants.SMS_CODE_EXPIRE_TIME/60)], 1)
        # except Exception, e:
        #     logging.error(e)
        #     resp = {
        #         'errno':RET.THIRDERR,
        #         'errmsg':'短信发送失败'
        #     }
        #     return self.write(resp)

        resp = {
            'errno':RET.OK,
            'errmsg':'短信发送成功',
            'data':sms_code
        }
        self.write(resp)

