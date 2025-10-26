from webtoolkit import (
   CrawlerInterface,
   PageResponseObject,
   PageRequestObject,
   get_default_user_agent,
   get_default_headers,
)


from webtoolkit.tests.fakeinternet import FakeInternetTestCase


class CrawlerInterfaceTest(FakeInternetTestCase):
    def test_constructor__url(self):
        test_url = "https://example.com"
        interface = CrawlerInterface(test_url)

        self.assertEqual(interface.request.url, test_url)

    def test_constructor__sets_request_url(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.request.url, test_url)

    def test_constructor__get_timeout(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.timeout_s = 666

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_timeout_s(), 666)

    def test_constructor__get_timeout__notimeout(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.timeout_s = None

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_timeout_s(), 20)

    def test_constructor__get_request_headers(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.request_headers = {"test": "test"}

        interface = CrawlerInterface(test_url, request=request)

        self.assertTrue(interface.get_request_headers())

    def test_constructor__get_request_headers_user_agent(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.user_agent = "Test-User-Agent"

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_request_headers()["User-Agent"], "Test-User-Agent")

    def test_constructor__get_bytes_limit(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.bytes_limit = 2160

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_bytes_limit(), 2160)

    def test_constructor__get_response_file(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.settings["response_file"] = "response_file.txt"

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_response_file(), "response_file.txt")

    def test_get_user_agent__default(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"

        interface = CrawlerInterface(test_url, request=request)

        self.assertTrue(interface.get_user_agent())

    def test_get_user_agent__not_default(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"
        request.user_agent = "Test-User-Agent"

        interface = CrawlerInterface(test_url, request=request)

        self.assertEqual(interface.get_user_agent(), "Test-User-Agent")

    def test_get_default_user_agent(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"

        interface = CrawlerInterface(test_url, request=request)

        self.assertTrue(interface.get_default_user_agent())

    def test_get_default_headers(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test Name"

        interface = CrawlerInterface(test_url, request=request)

        self.assertTrue(interface.get_default_headers())

    def test_get_accept_types(self):
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.accept_types = "text/html"

        interface = CrawlerInterface(test_url, request=request)

        self.assertTrue(interface.get_accept_types())

    def test_is_response_valid(self):
        response = PageResponseObject(status_code=200, text="test")
        test_url = "https://example.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "Test crawler"
        request.accept_types = "text/html"

        interface = CrawlerInterface(test_url, request=request)
        interface.response = response

        self.assertTrue(interface.is_response_valid())


class FunctionsTest(FakeInternetTestCase):
    def test_get_default_headers(self):

        # call tested function
        headers = get_default_headers()

        self.assertTrue(headers)
        self.assertTrue(len(headers) > 0)

        self.assertIn("User-Agent", headers)

    def test_get_default_user_agent(self):

        # call tested function
        user_agent = get_default_user_agent()

        self.assertTrue(user_agent)
