# -*- coding:utf-8 -*-

from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

#需要填写你的 Access Key 和 Secret Key

def upload2qiniu(file_data):
    '''上传到七牛服务器，直接上传图片文件的二进制数据'''

    access_key = 'SiMFc6qdoSqUjy0uXP_TYjh1J70E381zOUwJuEA2'
    secret_key = 'reode-W3bEHvn_C0oc57piit-_29zRidWjAGe710'
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'ihome'
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    ret, info = put_data(token, None, file_data)
    if 200 != info.status_code:
        # 上传到七牛出现异常，将异常抛出
        raise Exception('上传到七牛出现了异常')
    else:
        return ret['key']

if __name__ == '__main__':
    with open('我.jpg') as f:
        print upload2qiniu(f.read())

