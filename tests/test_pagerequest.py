from pathlib import Path
from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    PageRequestObject,
    RssPage,
    HtmlPage,

    request_to_json,
    request_encode,
    json_to_request,

    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
)

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class PageRequestObjectToJsonTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_url(self):
        request = PageRequestObject(url="https://test.com")
        json = request_to_json(request)

        self.assertEqual(json["url"], "https://test.com")


class PageRequestObjectFromJsonTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_url(self):
        json = {}
        json["url"] = "https://test.com"

        request = json_to_request(json)

        self.assertEqual(request.url, "https://test.com")


class PageRequestObjectEncodeTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_url(self):
        request = PageRequestObject(url="https://test.com")
        encoded = request_encode(request)

        self.assertEqual(encoded, "url=https%3A%2F%2Ftest.com")
