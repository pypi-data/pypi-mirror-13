# -*- coding: utf-8 -*-

import os
from datetime import datetime

import cos2


# 以下代码展示了一些和文件相关的高级用法，如中文、设置用户自定义元数据、拷贝文件、追加上传等。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
access_key_id = '39dafadad90942eea89e9fb8c7690877'
access_key_secret =  'f2ee0f5a04414277b73d800cbaec0836'
bucket_name = 'bbnn'
endpoint = 'http://cos-beta.chinac.com'



# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = cos2.Bucket(cos2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
#bucket.create_bucket()

print(bucket.get_object("pjlufmyzcppovamgxanfwcfz").content_length)
