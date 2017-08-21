# -*- coding:gbk -*-
# -*- coding:utf-8 -*-

from CCPRestSDK import REST
import ConfigParser
import logging

# ���ʺ�
accountSid = '8aaf07085d106c7f015d6340837d23db'

# ���ʺ�Token
accountToken = '10a68ba18e4140d685914ca90cfc846b'

# Ӧ��Id
appId = '8aaf07085d106c7f015d634083cc23e0'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'

class CCP(object):
    '''���Ͷ��ŵĸ�����'''
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '__instance'):
            return cls.__instance
        else:
            # ����CCP����󣬱��浽__instance��������
            cls.__instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls.__instance.rest = REST(serverIP, serverPort, softVersion)
            cls.__instance.rest.setAccount(accountSid, accountToken)
            cls.__instance.rest.setAppId(appId)
            return cls.__instance

    def send_templates_sms(self, to, datas, tmp_id):
        result = self.rest.sendTemplateSMS(to, datas, tmp_id)
        if result.get("statusCode") != "000000":
            # ��ʾ��ͨѶ���Ͷ���ʧ��
            reason = u"��ͨѶ���Ͷ���ʧ��: %s" % result.get("statusMsg")
            logging.error(reason)
            raise Exception(reason)

ccp = CCP()
if __name__ == '__main__':

    ccp.send_templates_sms('13426078791', ['123456', '5'], '1')
