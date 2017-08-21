# -*- coding:utf-8 -*-

import logging
import re
import constants

from bases import BaseHandler
from utils.response_code import RET
from utils.upload_image import upload2qiniu
from utils.commons import required_login


class AvatarHandler(BaseHandler):
    '''处理用户上传头像'''

    @required_login
    def put(self):
        '''处理图片文件'''

        # 获取用户信息
        try:
            user_id = self.session.data['user_id']
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.SESSIONERR, errmsg='获取用户数据失败'))

        # 获取头像图片信息
        pic_list = self.request.files.get('avatar')
        # 判断前端头像图片是否传递成功
        if pic_list:
            # 将图片的二进制数据上传至七牛服务器
            pic = pic_list[0]
            try:
                key = upload2qiniu(pic.body)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.THIRDERR, errmsg='头像上传失败!'))
            # 将用户上传头像key存入mysql数据库中
            sql = 'update ih_user_profile set up_avatar= %(key)s WHERE up_user_id=%(user_id)s;'
            try:
                self.db.execute(sql, key=key, user_id=user_id)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='头像上传失败!'))
            # 更新session中的图像url信息
            self.session.data['avatar'] = key
            try:
                self.session.save()
            except Exception, e:
                logging.error(e)
            return self.write(dict(errno=RET.OK, errmsg='头像上传成功!',
                                   avatar_url=constants.QINIU_URL_PREFIX+key))
        # 头像未传递到后端
        return self.write(dict(errno=RET.NODATA, errmsg='头像上传失败'))


class AuthHandler(BaseHandler):
    '''处理实名认证信息'''

    @required_login
    def get(self):
        '''查询用户实名认证信息'''
        user_id = self.session.data['user_id']
        sql = 'select up_real_name, up_id_card from ih_user_profile WHERE up_user_id=%s'
        try:
            result = self.db.get(sql, user_id)
        except Exception, e:
            logging.error(e)
            return self.write({'errno':RET.DBERR})
        return self.write(dict(
                errno=RET.OK,
                errmsg='ok',
                data=dict(
                    real_name=result['up_real_name'],
                    id_card=result['up_id_card']
                )
            ))

    @required_login
    def put(self):
        '''添加用户实名认证信息'''
        user_id = self.session.data['user_id']
        # 查询数据库中是否有实名认证记录,只有记录为空时才可实名认证
        sql = 'select up_user_id from ih_user_profile WHERE up_user_id=%s AND ' \
              ' up_real_name is NULL and up_id_card is NULL'
        try:
            result = self.db.get(sql, user_id)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='实名制信息查询失败'))
        if not result:
            return self.write(dict(errno=RET.DATAEXIST, errmsg='实名登记已存在，如需更改请联系客服！'))

        real_name = self.json_data.get('real_name')
        id_card = self.json_data.get('id_card')
        # 校验身份证号的合法性
        if not re.match(r'^[1-6][1-7][0-4]\d{3}[12]\d{11}$', id_card):
            return self.write(dict(errno=RET.PARAMERR, errmsg='身份证号输入有误!'))
        sql = 'update ih_user_profile set up_real_name=%(name)s, up_id_card=%(id)s' \
              ' where up_user_id=%(user_id)s'
        try:
            self.db.execute(sql, name=real_name, id=id_card, user_id=user_id)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='数据保存失败'))
        return self.write(dict(errno=RET.OK, errmsg='实名制信息保存成功!'))



