from webtools import (
    WebConfig,
)

from .fakeinternet import FakeInternetTestCase, MockRequestCounter


class WebConfigTest(FakeInternetTestCase):
    def test_get_bytes_limits(self):
        limit = WebConfig.get_bytes_limit()

        self.assertTrue(limit)
