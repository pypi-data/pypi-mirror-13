# -*- coding: utf-8 -*-

import os
from datetime import datetime

import cos2


# 以下代码展示了一些和文件相关的高级用法，如中文、设置用户自定义元数据、拷贝文件、追加上传等。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
access_key_id = 'AccessKeyId'
access_key_secret = 'AccessKeySecret'
bucket_name = 'BucketName'
endpoint = 'http://cos2-beta.chinac.com'



# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = cos2.Bucket(cos2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
#bucket.create_bucket()

result = bucket.put_object('111.txt', "Anything you're good at contributes to happiness.",
                           headers={'x-cos2-meta-author': 'Russell'})


