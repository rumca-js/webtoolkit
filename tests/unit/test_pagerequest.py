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
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.mocks import MockCrawler


class PageRequestObjectTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        self.ignore_memory = False
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()
        #print(f"Memory increase {memory_increase} setup")

    def tearDown(self):
        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)

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

    def test_get_proxies_map__noproxies(self):
        request = PageRequestObject(url="https://test.com")
        crawler = MockCrawler(request = request)
        request.crawler_type = crawler
        request.http_proxy = None
        request.https_proxy = None

        # call tested function
        proxies = request.get_proxies_map()

        self.assertTrue(proxies is None)

    def test_get_proxies_map__proxies(self):
        request = PageRequestObject(url="https://test.com")
        crawler = MockCrawler(request = request)
        request.crawler_type = crawler
        request.http_proxy = "http://192.168.0.1:8080"
        request.https_proxy = "https://8.8.8.8:8080"

        # call tested function
        proxies = request.get_proxies_map()

        self.assertIn("http", proxies)
        self.assertIn("https", proxies)

        self.assertEqual(proxies["http"], "http://192.168.0.1:8080")
        self.assertEqual(proxies["https"], "https://8.8.8.8:8080")
