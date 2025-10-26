from webtoolkit import PageRequestObject, DefaultUrlHandler, HttpPageHandler
from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockUrl, MockRequestCounter


class DefaultUrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_page_url(self):
        MockRequestCounter.mock_page_requests = 0

        test_url = "https://google.com"

        request = PageRequestObject(test_url)
        request.handler_type = None

        handler = DefaultUrlHandler(test_url, request=request, url_builder=MockUrl)

        # call tested function
        url = handler.get_page_url("https://example.com")

        self.assertTrue(url)
        self.assertEqual(url.request.url, "https://example.com")
        self.assertEqual(url.request.handler_type, HttpPageHandler)

        self.assertEqual(handler.url, test_url)
