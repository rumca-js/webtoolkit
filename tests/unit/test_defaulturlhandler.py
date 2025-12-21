from webtoolkit import PageRequestObject, DefaultUrlHandler, HttpPageHandler
from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockUrl, MockRequestCounter


class DefaultUrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_page_url__same_url_uses_input_request(self):
        MockRequestCounter.mock_page_requests = 0

        test_url = "https://google.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "test1"
        request.crawler_type = None
        request.handler_name = "test2"
        request.handler_type = None
        request.cookies = {"CONSENT" : "test-YES"}

        handler = DefaultUrlHandler(test_url, request=request, url_builder=MockUrl)

        # call tested function
        url = handler.get_page_url("https://google.com")

        self.assertTrue(url)
        self.assertEqual(url.request.url, "https://google.com")
        # self.assertEqual(url.request.crawler_name, "test1") # may be overwritten by unit test builder
        # self.assertFalse(url.request.crawler_type) # may be overwritten by unit test builder
        self.assertEqual(url.request.handler_name, "HttpPageHandler")
        self.assertFalse(url.request.handler_type)
        self.assertIn("CONSENT", url.request.cookies)

        self.assertEqual(handler.url, test_url)

    def test_get_page_url__different_url_uses_input_request(self):
        MockRequestCounter.mock_page_requests = 0

        test_url = "https://google.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "test1"
        request.crawler_type = None
        request.handler_name = "test2"
        request.handler_type = None
        request.cookies = {"CONSENT" : "test-YES"}

        handler = DefaultUrlHandler(test_url, request=request, url_builder=MockUrl)

        # call tested function
        url = handler.get_page_url("https://example.com")

        self.assertTrue(url)
        self.assertEqual(url.request.url, "https://example.com")
        # self.assertEqual(url.request.crawler_name, "test1") # may be overwritten by unit test builder
        # self.assertFalse(url.request.crawler_type) # may be overwritten by unit test builder
        self.assertEqual(url.request.handler_name, "HttpPageHandler")
        self.assertFalse(url.request.handler_type)
        self.assertNotIn("CONSENT", url.request.cookies)

        self.assertEqual(handler.url, test_url)

    def test_build_default_url__same_url_uses_input_request(self):
        MockRequestCounter.mock_page_requests = 0

        test_url = "https://www.youtube.com/watch?v=1234"

        request = PageRequestObject(test_url)
        request.crawler_name = "test1"
        request.crawler_type = None
        request.handler_name = "test2"
        request.handler_type = None
        request.cookies = {"CONSENT" : "test-YES"}

        handler = DefaultUrlHandler(test_url, request=request, url_builder=MockUrl)

        # call tested function
        url = handler.build_default_url("https://www.youtube.com/watch?v=1234")

        self.assertTrue(url)
        self.assertEqual(url.request.url, "https://www.youtube.com/watch?v=1234")
        # self.assertEqual(url.request.crawler_name, "test1") # may be overwritten by unit test builder
        # self.assertFalse(url.request.crawler_type) # may be overwritten by unit test builder
        self.assertFalse(url.request.handler_name)
        self.assertFalse(url.request.handler_type)
        self.assertIn("CONSENT", url.request.cookies)

        self.assertEqual(handler.url, test_url)

    def test_build_default_url__same_url_uses_input_request(self):
        MockRequestCounter.mock_page_requests = 0

        test_url = "https://google.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "test1"
        request.crawler_type = None
        request.handler_name = "test2"
        request.handler_type = None
        request.cookies = {"CONSENT" : "test-YES"}

        handler = DefaultUrlHandler(test_url, request=request, url_builder=MockUrl)

        # call tested function
        url = handler.build_default_url("https://www.youtube.com/watch?v=1234")

        self.assertTrue(url)
        self.assertEqual(url.request.url, "https://www.youtube.com/watch?v=1234")
        # self.assertEqual(url.request.crawler_name, "test1") # may be overwritten by unit test builder
        # self.assertFalse(url.request.crawler_type) # may be overwritten by unit test builder
        self.assertFalse(url.request.handler_name)
        self.assertFalse(url.request.handler_type)
        self.assertNotIn("CONSENT", url.request.cookies)

        self.assertEqual(handler.url, test_url)
