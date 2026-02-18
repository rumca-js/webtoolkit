import gc
from webtoolkit import (
   HtmlPage,
   RssPage,
   HttpPageHandler,
   HTTP_STATUS_CODE_SERVER_ERROR,
   HTTP_STATUS_OK,
)
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockRequestCounter, MockUrl


class HttpPageHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        self.ignore_memory = False
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()

    def tearDown(self):
        MockRequestCounter.reset()
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)

    def test_constructor(self):
        test_link = "https://linkedin.com"
        request = MockUrl(test_link).get_init_request()

        # call tested function
        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        self.assertTrue(handler)

    def test_get_page_handler__html(self):
        test_link = "https://linkedin.com"
        self.ignore_memory = True
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), HtmlPage)

    def test_get_page_handler__rss(self):
        self.ignore_memory = True

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

    def test_get_contents__html(self):
        self.ignore_memory = True
        test_link = "https://linkedin.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        self.assertTrue(handler.get_contents())

    def test_get_response__html(self):
        test_link = "https://linkedin.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        self.assertTrue(handler.get_response())

    def test_get_response__rss(self):
        test_link = "https://www.reddit.com/r/searchengines/.rss"
        request = MockUrl(test_link).get_init_request()

        self.ignore_memory = True

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        self.assertTrue(handler.get_response())

    def test_get_response__calls_crawler(self):
        MockRequestCounter.reset()

        test_link = "https://x.com/feed"
        request = MockUrl(test_link).get_init_request()
        request.timeout_s = 120

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
        response = handler.get_response()

        self.assertEqual(len(MockRequestCounter.request_history), 1)
        self.assertIn("url", MockRequestCounter.request_history[0])
        self.assertEqual(MockRequestCounter.request_history[0]["url"], test_link)
        self.assertIn("crawler_data", MockRequestCounter.request_history[0])

        request = MockRequestCounter.request_history[0]["crawler_data"]
        self.assertEqual(request.timeout_s, 120)

    def test_get_response__no_request(self):
        MockRequestCounter.reset()

        test_link = "https://x.com/feed"

        handler = HttpPageHandler(test_link, request=None, url_builder = MockUrl)
        response = handler.get_response()

        # no crawler was specified - we don't know what to do

        self.assertEqual(response.get_status_code(), HTTP_STATUS_CODE_SERVER_ERROR)
        self.assertEqual(len(response.errors), 1)

    def test_is_handled_by(self):
        test_link = "http://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = MockUrl)

        self.assertTrue(handler.is_handled_by())

        test_link = "https://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = MockUrl)

        self.assertTrue(handler.is_handled_by())

        test_link = "ftp://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = MockUrl)

        self.assertFalse(handler.is_handled_by())

    def test_get_page_handler__broken_content_type(self):
        # TODO analyze why so much additional memory is left in
        self.ignore_memory = True

        test_link = "https://rss-page-with-broken-content-type.com/feed"
        # even though it is HTML in contents type, it is correctly read as RssPage
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
        response = handler.get_response()

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

        self.assertEqual(response.get_content_type(), "text/html")

    def test_get_hash(self):
        self.ignore_memory = True
        test_link = "https://linkedin.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        hash = handler.get_hash()

        self.assertTrue(hash)

    def test_get_body_hash(self):
        self.ignore_memory = True
        test_link = "https://linkedin.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)

        # call tested function
        hash = handler.get_body_hash()

        self.assertTrue(hash)

    def test_canonical_url__valid(self):
        self.ignore_memory = True
        MockRequestCounter.reset()

        test_link = "https://page-with-canonical-link.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
        response = handler.get_response()

        self.assertEqual(response.get_status_code(), HTTP_STATUS_OK)
        self.assertEqual(handler.get_canonical_url(), "https://www.page-with-canonical-link.com")

    def test_canonical_url__nocanonical(self):
        self.ignore_memory = True
        MockRequestCounter.reset()

        test_link = "https://page-without-canonical-link.com"
        request = MockUrl(test_link).get_init_request()

        handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
        response = handler.get_response()

        self.assertEqual(response.get_status_code(), HTTP_STATUS_OK)
        self.assertFalse(handler.get_canonical_url())


class HttpPageHandlerMemoryTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        self.ignore_memory = False
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()

    def tearDown(self):
        MockRequestCounter.reset()
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)

    def test_get_response__html(self):
        for i in range(1, 3500):
            test_link = "https://linkedin.com"
            url = MockUrl(test_link)
            request = url.get_init_request()

            handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
            response = handler.get_response()
            url.close()
