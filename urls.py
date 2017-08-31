# -*- coding:utf-8 -*-

import os
from handler.bases import GetXsrfCookie, StaticHandler
from handler import verify_code, passport, profile, house

urls = [
    # 用户部分
    (r'/api/v1.0/imagecode', verify_code.ImageCodeHandler), # 图片验证码
    (r'/api/v1.0/smscode', verify_code.SMSCodeHandler), # 短信验证码
    (r'/api/v1.0/mobile', passport.MobileAjaxHandler), # 检验手机号是否注册过
    (r'/api/v1.0/user', passport.UserHandler), # 注册put/获取用户信息get/修改用户信息post
    (r'/api/v1.0/session', passport.SessionHandler), # 登录put/登出delete/查询登录状态get
    (r'/api/v1.0/avatar', profile.AvatarHandler), # 上传头像
    (r'/api/v1.0/auth', profile.AuthHandler), # 实名认证

    # 房屋部分
    (r'/api/v1.0/areas', house.AreasHandler), # 获取房源城区信息
    (r'/api/v1.0/houses$', house.HouseHandler), # 处理房屋信息
    (r'/api/v1.0/houses/images', house.HouseImageHandler), # 上传房屋图片
    (r'/api/v1.0/houses/users', house.UserHouseHandler), # 查询当前用户房屋信息
    (r'/api/v1.0/houses/detail', house.HouseDetailHandler), # 房屋详情页



    # 定义静态网页访问路由地址
    (r'/(.*)', StaticHandler, {'path':os.path.join(os.path.dirname(__file__), 'html'),
    'default_filename':'index.html'}),
    (r'/xsrf', GetXsrfCookie),  # xsrf接口
]