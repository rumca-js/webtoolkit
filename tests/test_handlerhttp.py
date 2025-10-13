from webtoolkit import (
   HtmlPage,
   RssPage,
   HttpPageHandler,
   RemoteUrl,
   CrawlerInterface,
   PageResponseObject,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from tests.fakeinternetdata import webpage_simple_rss_page


# TODO implmeent
class Crawler(CrawlerInterface):
    mock_counter = 0

    def __init__(self, url):
        super().__init__(url=url)

    def run(self):
        Crawler.mock_counter += 1

        headers = {
            "Content-Type" : "text/html"
        }
        text = "test"

        if self.request.url == "https://www.reddit.com/r/searchengines/.rss":
            text = webpage_simple_rss_page

        self.response = PageResponseObject(url=self.request.url, status_code=200, text="text", headers=headers)
        return self.response

    def reset():
        Crawler.mock_counter = 0


def get_init_settings(url):
    return {
            "name" : "something",
            "crawler"  :Crawler(url),
            "settings" : {},
    }


class HttpPageHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        # call tested function
        handler = HttpPageHandler(test_link, settings = settings)

        self.assertTrue(handler)

    def test_get_page_handler__html(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), HtmlPage)

    def test_get_page_handler__rss(self):
        test_link = "https://www.reddit.com/r/searchengines/.rss"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

    def test_get_page_handler__broken_content_type(self):
        test_link = "https://rss-page-with-broken-content-type.com/feed"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)
        response = handler.get_response()

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

        self.assertEqual(response.get_content_type(), "text/html")

    def test_get_contents_hash(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)

    def test_get_contents_body_hash(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)

    def test_get_contents__html(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        self.assertTrue(handler.get_contents())

    def test_get_response__html(self):
        test_link = "https://linkedin.com"
        settings = get_init_settings(test_link)

        handler = HttpPageHandler(test_link, settings = settings)

        # call tested function
        self.assertTrue(handler.get_response())

    def test_is_handled_by(self):
        test_link = "http://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link)

        self.assertTrue(handler.is_handled_by())

        test_link = "https://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link)

        self.assertTrue(handler.is_handled_by())

        test_link = "ftp://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link)

        self.assertFalse(handler.is_handled_by())

    def test_get_response__calls_crawler(self):
        Crawler.reset()

        test_link = "https://x.com/feed"
        settings = get_init_settings(test_link)
        settings["settings"]["timeout_s"] = 120

        handler = HttpPageHandler(test_link, settings = settings)
        response = handler.get_response()

        self.assertEqual(Crawler.mock_counter, 1)
