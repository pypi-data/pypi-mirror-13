import json
from django.test import TestCase

from shanbay_api.response import SuccessResult, FailedResult, BadRequestResult, ForbiddenResult, NotFoundResult, DuplicatedResult, NotHereResult, InternalErrorResult


class APITest(TestCase):
    def test_login_required(self):
        res = self.client.get('/api/v2/login_required_test/')
        self.assertEqual(res.status_code, 401)

    def test_response(self):
        res = self.client.get('/api/v2/test/')
        content = json.loads(res.content.decode('utf-8'))
        self.assertEqual(content['status_code'], 0)

        res = self.client.post('/api/v2/test/')
        content = json.loads(res.content.decode('utf-8'))
        self.assertEqual(content['status_code'], 1)
