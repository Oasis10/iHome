# -*- coding:utf-8 -*-
import json
import logging

import constants
from bases import BaseHandler
from utils.commons import required_login
from utils.response_code import RET
from utils.upload_image import upload2qiniu


class AreasHandler(BaseHandler):
    '''房源城区信息'''
    def get(self):
        '''查询具体城区信息'''

        # 首先查询缓存中是否有城区信息
        try:
            result = self.redis.get('areas_info')
        except Exception, e:
            logging.error(e)
        else:
            if result:
                logging.info('hit redis areas_info')
                return self.write(dict(errno=RET.OK, errmsg='ok', data=json.loads(result)))

        # 如果缓存中未查询到城区信息
        sql = 'select ai_area_id as aid, ai_name as aname from ih_area_info;'
        try:
            # 使用query方法查询,返回的是一个列表,包含每一个字典
            result = self.db.query(sql)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='查询数据失败'))

        # 将result数据转为json格式
        result_json = json.dumps(result)
        # 将result城区信息存入redis数据库中,用作缓存信息使用处理
        try:
            self.redis.setex('areas_info', constants.AREAS_INFO_EXPIRE_TIME, result_json)
        except Exception, e:
            logging.error(e)

        return self.write(dict(errno=RET.OK, errmsg='ok', data=result))


class HouseHandler(BaseHandler):
    '''房屋信息'''

    @required_login
    def put(self):
        '''提交新房源'''
        user_id = self.session.data['user_id']
        # 前端发送过来的json数据的样例
        # {
        #     "title": "",
        #     "price": "",
        #     "area_id": "1",
        #     "address": "",
        #     "room_count": "",
        #     "acreage": "",
        #     "unit": "",
        #     "capacity": "",
        #     "beds": "",
        #     "deposit": "",
        #     "min_days": "",
        #     "max_days": "",
        #     "facility": ["7", "8"]
        # }

        title = self.json_data.get('title')
        price = self.json_data.get('price')
        area_id = self.json_data.get('area_id')
        address = self.json_data.get('address')
        room_count = self.json_data.get('room_count')
        acreage = self.json_data.get('acreage')
        unit = self.json_data.get('unit')
        capacity = self.json_data.get('capacity')
        beds = self.json_data.get('beds')
        deposit = self.json_data.get('deposit')
        min_days = self.json_data.get('min_days')
        max_days = self.json_data.get("max_days")

        if not all([title, price, area_id, address, room_count,
                    acreage, unit, capacity, beds, deposit, min_days]):
            return self.write(dict(errno=RET.PARAMERR, errmsg='参数不完整'))

        # 将价格转为分(整型)
        try:
            price = int(float(price)*100)
            deposit = int(float(deposit)*100)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.PARAMERR, errmsg='参数错误'))

        # 将房屋数据存入mysql数据库
        sql = 'insert into ih_house_info (hi_user_id, hi_title, hi_price, hi_area_id, hi_address, hi_room_count, ' \
              'hi_acreage, hi_house_unit, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days) VALUES (%(user_id)s, %(title)s' \
              ',%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(acreage)s,%(unit)s,%(capacity)s,%(beds)s,' \
              '%(deposit)s,%(min_days)s,%(max_days)s)'

        try:
            house_id = self.db.execute(sql, user_id=user_id, title=title, price=price, area_id=area_id, address=address,
                                       room_count=room_count, acreage=acreage, unit=unit, capacity=capacity,
                                       beds=beds, deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception, e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='房屋信息保存失败'))

        # 房屋详细设施
        facility = self.json_data.get('facility', [])
        if facility:
            # 构造sql语句
            sql = 'insert into ih_house_facility (hf_house_id, hf_facility_id) VALUES '
            # 存储sql语句占位符
            sql_str_list = []
            # 存储sql语句动态参数
            sql_val_list = []
            # 遍历房屋设施参数
            for facility_id in facility:
                sql_str_list.append('(%s,%s)')
                sql_val_list.append(house_id)
                sql_val_list.append(facility_id)

            # 拼接sql语句
            sql += ','.join(sql_str_list)
            try:
                self.db.execute(sql, *tuple(sql_val_list))
            except Exception, e:
                logging.error(e)
                # 保存房屋设施信息失败,手动执行事务回滚
                sql = 'delete from ih_house_info WHERE hi_house_id=%s'
                try:
                    self.db.execute_rowcount(sql, house_id)
                except Exception, e:
                    logging.error(e)
                    return self.write(dict(errno=RET.DBERR, errmsg='保存房屋信息失败'))
                else:
                    return self.write(dict(errno=RET.DBERR, errmsg='删除房屋设施信息成功'))

            return self.write(dict(errno=RET.OK, errmsg='ok', house_id=house_id))



class HouseImageHandler(BaseHandler):
    '''上传房屋图片'''

    def put(self):
        house_id = self.get_argument('house_id')
        house_image_list = self.request.files.get('house_image')
        # 判断是否接收到了图片
        if house_image_list:
            image = house_image_list[0].body
            # 上传到七牛服务器
            try:
                key = upload2qiniu(image)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.THIRDERR, errmsg='上传房屋图片失败'))
            sql = 'insert into ih_house_image(hi_house_id, hi_url) values(%(house_id)s, %(url)s);' \
                  'update ih_house_info set hi_index_image_url=%(url)s WHERE hi_house_id=%(house_id)s'
            url = constants.QINIU_URL_PREFIX + key
            try:
                self.db.execute(sql, url=url, house_id=house_id)
            except Exception, e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='保存图片url失败'))
            return self.write(dict(
                errno=RET.OK,
                errmsg='ok',
                url = url
            ))
        return self.write(dict(errno=RET.PARAMERR, errmsg='参数缺失'))


class UserHouseHandler(BaseHandler):
    '''处理用户的房屋信息'''

    @required_login
    def get(self):
        '''获取用户房屋信息'''
        # house_id
        # title
        # image_url
        # area
        # price
        # time
        user_id = self.session.data['user_id']
        # 查询用户名下房源信息
        sql = "select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url " \
              "from ih_house_info a left join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s;"
        sql = 'select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,a.hi_index_image_url,b.ai_name ' \
              'from ih_house_info a LEFT JOIN '









