# -*- coding: utf-8 -*-

import time
import os
import json

import cos2
from itertools import islice


# 以下代码展示了Bucket相关操作，诸如创建、删除、列举Bucket等。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
access_key_id = 'AccessKeyId'
access_key_secret = 'AccessKeySecret'
bucket_name = 'BucketName'
endpoint = 'http://cos2-beta.chinac.com'

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = cos2.Bucket(cos2.Auth(access_key_id, access_key_secret), endpoint,bucket_name)
bucket.put_bucket_acl('public-read')







