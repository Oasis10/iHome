# -*- coding:gbk -*-
# -*- coding:utf-8 -*-

from CCPRestSDK import REST
import ConfigParser
import logging

# 主帐号
accountSid = '8aaf07085d106c7f015d6340837d23db'

# 主帐号Token
accountToken = '10a68ba18e4140d685914ca90cfc846b'

# 应用Id
appId = '8aaf07085d106c7f015d634083cc23e0'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

class CCP(object):
    '''发送短信的辅助类'''
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '__instance'):
            return cls.__instance
        else:
            # 创建CCP类对象，保存到__instance类属性中
            cls.__instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls.__instance.rest = REST(serverIP, serverPort, softVersion)
            cls.__instance.rest.setAccount(accountSid, accountToken)
            cls.__instance.rest.setAppId(appId)
            return cls.__instance

    def send_templates_sms(self, to, datas, tmp_id):
        result = self.rest.sendTemplateSMS(to, datas, tmp_id)
        if result.get("statusCode") != "000000":
            # 表示云通讯发送短信失败
            reason = u"云通讯发送短信失败: %s" % result.get("statusMsg")
            logging.error(reason)
            raise Exception(reason)

ccp = CCP()
if __name__ == '__main__':

    ccp.send_templates_sms('13426078791', ['123456', '5'], '1')
