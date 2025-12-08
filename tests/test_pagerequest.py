from pathlib import Path
from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    PageRequestObject,
    RssPage,
    HtmlPage,

    request_to_json,
    request_encode,
    json_to_request,
    copy_request,

    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
)

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.mocks import MockCrawler


class PageRequestObjectTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_request_to_json(self):
        request = PageRequestObject(url="https://test.com")
        # call tested function
        json = request_to_json(request)

        self.assertEqual(json["url"], "https://test.com")

    def test_json_to_request(self):
        json = {}
        json["url"] = "https://test.com"

        # call tested function
        request = json_to_request(json)

        self.assertEqual(request.url, "https://test.com")

    def test_request_encode(self):
        request = PageRequestObject(url="https://test.com")
        # call tested function
        encoded = request_encode(request)

        self.assertEqual(encoded, "url=https%3A%2F%2Ftest.com")

    def test_copy_request(self):
        request = PageRequestObject(url="https://test.com")
        crawler = MockCrawler(request = request)
        request.crawler_type = crawler

        # call tested function
        request_copy = copy_request(request)

        self.assertEqual(request.url, request_copy.url)
        self.assertNotEqual(request.crawler_type, request_copy.crawler_type)
