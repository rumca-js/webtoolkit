from webtoolkit import CrawlerInterface, PageResponseObject

from tests.fakeinternet import FakeInternetTestCase

class CrawlerInterfaceTest(FakeInternetTestCase):
    def test_constructor__url(self):
        test_url = "https://example.com"
        interface = CrawlerInterface(test_url)

        self.assertEqual(interface.request.url, test_url)

    def test_constructor__settings__no_innersettings(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.request.url, test_url)

    def test_constructor__sets_request_url(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.request.url, test_url)

    def test_constructor__get_timeout(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.get_timeout_s(), 666)

    def test_constructor__get_timeout__notimeout(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.get_timeout_s(), 20)

    def test_constructor__get_request_headers(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "request_headers": {"test": "test"}
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertTrue(interface.get_request_headers())

    def test_constructor__get_request_headers_user_agent(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "request_headers": {"test": "test"},
               "User-Agent" : "Test-User-Agent"
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.get_request_headers()["User-Agent"], "Test-User-Agent")

    def test_constructor__get_bytes_limit(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "bytes_limit" : 2160
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.get_bytes_limit(), 2160)

    def test_constructor__get_response_file(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "response_file": "response_file.txt"
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertEqual(interface.get_response_file(), "response_file.txt")

    def test_get_default_user_agent(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertTrue(interface.get_default_user_agent())

    def test_get_default_headers(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertTrue(interface.get_default_headers())

    def test_get_accept_types(self):
        test_url = "https://example.com"
        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "accept_content_types": "text/html"
           }
        }
        interface = CrawlerInterface(test_url, settings=settings)

        self.assertTrue(interface.get_accept_types())

    def test_is_response_valid(self):
        response = PageResponseObject(status_code=200, text="test")
        test_url = "https://example.com"

        settings = {
           "name" : "Test name",
           "crawler" : "Test crawler",
           "settings" : {
               "timeout_s" : 666,
               "accept_content_types": "text/html"
           }
        }

        interface = CrawlerInterface(test_url, settings=settings)
        interface.response = response

        self.assertTrue(interface.is_response_valid())
