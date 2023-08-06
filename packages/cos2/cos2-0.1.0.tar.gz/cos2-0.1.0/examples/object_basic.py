# -*- coding: utf-8 -*-

import os
import shutil

import cos2


# 以下代码展示了基本的文件上传、下载、罗列、删除用法。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
#
# 以杭州区域为例，Endpoint可以是：
#   http://cos2.chinac.com
#   https://cos2.chinac.com
# 分别以HTTP、HTTPS协议访问。
access_key_id = 'AccessKeyId'
access_key_secret = 'AccessKeySecret'
bucket_name = 'BucketName'
endpoint = 'http://cos2-beta.chinac.com'



# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = cos2.Bucket(cos2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
bucket.create_bucket()
bucket.put_object_from_file('aaa.txt', 'test.txt')
assert not bucket.object_exists('aaa.txt')