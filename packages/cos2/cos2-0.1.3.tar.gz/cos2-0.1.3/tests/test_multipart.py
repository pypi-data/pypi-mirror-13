# -*- coding: utf-8 -*-

import unittest
import cos2

from common  import *
from cos2 import utils



class TestMultipart(CosTestCase):
    def test_multipart(self):
        key = self.random_key()
        content = random_bytes(5 * 1024 * 1024)

        parts = []
        upload_id = self.bucket.init_multipart_upload(key).upload_id

        result = self.bucket.upload_part(key, upload_id, 1, content)
        parts.append(cos2.models.PartInfo(1, result.etag))

        self.bucket.complete_multipart_upload(key, upload_id, parts)

        result = self.bucket.get_object(key)
        self.assertEqual(utils.content_md5(content), utils.content_md5(result.read()))



if __name__ == '__main__':
    unittest.main()