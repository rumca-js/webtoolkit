from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    is_status_code_valid,
    is_status_code_invalid,
)
from webtoolkit.statuses import *

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class StatusesTest(FakeInternetTestCase):
    def test_is_status_code_valid(self):
        self.assertFalse(is_status_code_valid(0))
        self.assertFalse(is_status_code_valid(199))

        self.assertTrue(is_status_code_valid(200))
        self.assertTrue(is_status_code_valid(201))
        self.assertTrue(is_status_code_valid(299))
        self.assertTrue(is_status_code_valid(300))
        self.assertTrue(is_status_code_valid(301))
        self.assertTrue(is_status_code_valid(399))

        self.assertFalse(is_status_code_valid(400))
        self.assertFalse(is_status_code_valid(401))
        self.assertFalse(is_status_code_valid(HTTP_STATUS_USER_AGENT))
        self.assertFalse(is_status_code_valid(404))
        self.assertFalse(is_status_code_valid(500))
        self.assertFalse(is_status_code_valid(600))
        self.assertFalse(is_status_code_valid(HTTP_STATUS_TOO_MANY_REQUESTS))
        self.assertFalse(is_status_code_valid(HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS))

    def test_is_status_code_invalid(self):
        self.assertFalse(is_status_code_invalid(0))
        self.assertTrue(is_status_code_invalid(199))

        self.assertFalse(is_status_code_invalid(200))
        self.assertFalse(is_status_code_invalid(201))
        self.assertFalse(is_status_code_invalid(299))
        self.assertFalse(is_status_code_invalid(300))
        self.assertFalse(is_status_code_invalid(301))
        self.assertFalse(is_status_code_invalid(399))

        self.assertTrue(is_status_code_invalid(400))
        self.assertFalse(is_status_code_invalid(HTTP_STATUS_USER_AGENT))
        self.assertTrue(is_status_code_invalid(404))
        self.assertFalse(is_status_code_invalid(HTTP_STATUS_TOO_MANY_REQUESTS))
        self.assertFalse(is_status_code_invalid(HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS))
        self.assertFalse(is_status_code_invalid(HTTP_STATUS_CODE_SERVER_ERROR))
