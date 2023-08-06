# -*- coding: utf-8 -*-

import datetime

from mock import patch
from functools import partial

from cos2 import to_string
from common import *


def all_tags(parent, tag):
    return [to_string(node.text) or '' for node in parent.findall(tag)]


def r4get_meta(body, in_status=200, in_headers=None):
    headers = cos2.CaseInsensitiveDict({
        'Server': 'ChinacCOS',
        'Date': 'Fri, 11 Dec 2015 11:40:31 GMT',
        'Content-Type': 'application/xml',
        'Content-Length': str(len(body)),
        'Connection': 'keep-alive',
        'x-cos-request-id': '566AB62EB06147681C283D73'
    })

    merge_headers(headers, in_headers)

    return MockResponse(in_status, headers, body)


class TestBucket(CosTestCase):
    @patch('cos2.Session.do_request')
    def test_create(self, do_request):
        resp = r4put(in_headers={'Location': '/ming-cos2-share'})
        do_request.return_value = resp

        result = bucket().create_bucket(cos2.BUCKET_ACL_PRIVATE)
        self.assertEqual(resp.headers['x-cos-request-id'], result.request_id)

    @patch('cos2.Session.do_request')
    def test_put_acl(self, do_request):
        req_info = RequestInfo()

        do_request.auto_spec = True
        do_request.side_effect = partial(do4put, req_info=req_info, data_type=DT_BYTES)

        bucket().put_bucket_acl(cos2.BUCKET_ACL_PRIVATE)
        self.assertEqual(req_info.req.headers['x-cos-acl'], 'private')

        bucket().put_bucket_acl(cos2.BUCKET_ACL_PUBLIC_READ)
        self.assertEqual(req_info.req.headers['x-cos-acl'], 'public-read')

        bucket().put_bucket_acl(cos2.BUCKET_ACL_PUBLIC_READ_WRITE)
        self.assertEqual(req_info.req.headers['x-cos-acl'], 'public-read-write')

    @patch('cos2.Session.do_request')
    def test_get_acl(self, do_request):
        template = '''<?xml version="1.0" encoding="UTF-8"?>
        <AccessControlPolicy>
            <Owner>
                <ID>1047205513514293</ID>
                <DisplayName>1047205513514293</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>{0}</Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''

        for permission in ['private', 'public-read', 'public-read-write']:
            do_request.return_value = r4get_meta(template.format(permission))
            self.assertEqual(bucket().get_bucket_acl().acl, permission)

    @patch('cos2.Session.do_request')
    def test_put_logging(self, do_request):
        req_info = RequestInfo()

        do_request.auto_spec = True
        do_request.side_effect = partial(do4put, req_info=req_info, data_type=DT_BYTES)

        template = '<BucketLoggingStatus><LoggingEnabled><TargetBucket>fake-bucket</TargetBucket>' + \
                   '<TargetPrefix>{0}</TargetPrefix></LoggingEnabled></BucketLoggingStatus>'

        target_bucket_name = 'fake-bucket'
        for prefix in [u'日志+/', 'logging/', '日志+/']:
            bucket().put_bucket_logging(cos2.models.BucketLogging(target_bucket_name, prefix))
            self.assertXmlEqual(req_info.data, template.format(to_string(prefix)))

    @patch('cos2.Session.do_request')
    def test_delete_logging(self, do_request):
        do_request.return_value = r4put()

        result = bucket().delete_bucket_logging()
        self.assertEqual(result.request_id, REQUEST_ID)

    @patch('cos2.Session.do_request')
    def test_get_logging(self, do_request):
        target_bucket_name = 'fake-bucket'

        template = '''<?xml version="1.0" encoding="UTF-8"?>
        <BucketLoggingStatus>
            <LoggingEnabled>
                <TargetBucket>fake-bucket</TargetBucket>
                <TargetPrefix>{0}</TargetPrefix>
            </LoggingEnabled>
        </BucketLoggingStatus>'''

        for prefix in [u'日志%+/*', 'logging/', '日志%+/*']:
            do_request.return_value = r4get_meta(template.format(to_string(prefix)))
            result = bucket().get_bucket_logging()

            self.assertEqual(result.target_bucket, target_bucket_name)
            self.assertEqual(result.target_prefix, to_string(prefix))

    @patch('cos2.Session.do_request')
    def test_put_website(self, do_request):
        req_info = RequestInfo()

        do_request.auto_spec = True
        do_request.side_effect = partial(do4put, req_info=req_info, data_type=DT_BYTES)

        template = '<WebsiteConfiguration><IndexDocument><Suffix>{0}</Suffix></IndexDocument>' + \
            '<ErrorDocument><Key>{1}</Key></ErrorDocument></WebsiteConfiguration>'

        for index, error in [('index+中文.html', 'error.中文') ,(u'中-+()文.index', u'@#$%中文.error')]:
            bucket().put_bucket_website(cos2.models.BucketWebsite(index, error))
            self.assertXmlEqual(req_info.data, template.format(to_string(index), to_string(error)))

    @patch('cos2.Session.do_request')
    def test_get_website(self, do_request):
        template = '<WebsiteConfiguration><IndexDocument><Suffix>{0}</Suffix></IndexDocument>' + \
            '<ErrorDocument><Key>{1}</Key></ErrorDocument></WebsiteConfiguration>'

        for index, error in [('index+中文.html', 'error.中文') ,(u'中-+()文.index', u'@#$%中文.error')]:
            do_request.return_value = r4get_meta(template.format(to_string(index), to_string(error)))

            result = bucket().get_bucket_website()
            self.assertEqual(result.index_file, to_string(index))
            self.assertEqual(result.error_file, to_string(error))

    @patch('cos2.Session.do_request')
    def test_delete_website(self, do_request):
        do_request.return_value = r4put()

        result = bucket().delete_bucket_website()
        self.assertEqual(result.request_id, REQUEST_ID)



    @patch('cos2.Session.do_request')
    def test_get_location(self, do_request):
        body = b'''<?xml version="1.0" encoding="UTF-8"?>
        <LocationConstraint>cos2-cn-hangzhou</LocationConstraint>'''

        do_request.return_value = r4get_meta(body)

        result = bucket().get_bucket_location()
        self.assertEqual(result.location, 'cos2-cn-hangzhou')

if __name__ == '__main__':
    unittest.main()