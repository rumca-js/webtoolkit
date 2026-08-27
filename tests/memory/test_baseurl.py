"""
This test uses MockUrl to test BaseUrl, because some of BaseUrl functions need to be overriden.

@note some tests do not check memory as it is not reliable
"""

import gc
import json
from webtoolkit import (
    HttpPageHandler,
    HtmlPage,
    RssPage,
    PageResponseObject,
    PageRequestObject,
    RedditUrlHandler,
    YouTubeChannelHandler,
    YouTubeVideoHandler,
    BaseUrl,
    RemoteServer,
    RemoteUrl,
)
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockRequestCounter, MockCrawler, MockUrl


class BaseUrlMemoryTest(FakeInternetTestCase):
    """
    I think that after 1k of responses it should indicate memory errors
    """
    def setUp(self):
        self.disable_web_pages()

        self.ignore_memory = True # TODO fix
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()
        self.iteration_count = 500

    def tearDown(self):
        MockRequestCounter.reset()
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)

    def get_request(self, url):
        request = PageRequestObject(url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url)
        return request

    def test_get_response__html(self):
        MockRequestCounter.mock_page_requests = 0

        if not self.is_memory_test():
            return

        for i in range(1, self.iteration_count):
            test_link ="https://linkedin.com"
            url = MockUrl(request=self.get_request(test_link))
            response = url.get_response()
            url.close()

        print("OK")

    def test_get_response__rss(self):
        MockRequestCounter.mock_page_requests = 0

        if not self.is_memory_test():
            return

        for i in range(1, self.iteration_count):
            test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"
            url = MockUrl(request=self.get_request(test_link))
            response = url.get_response()
            url.close()

        print("OK")

    def test_get_response__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        if not self.is_memory_test():
            return

        for i in range(1, self.iteration_count):
            test_link = "https://www.reddit.com/r/searchengines/.rss"
            url = MockUrl(request=self.get_request(test_link))
            response = url.get_response()
            url.close()

        print("OK")

    def test_get_response__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        if not self.is_memory_test():
            return

        for i in range(1, self.iteration_count):
            test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
            url = MockUrl(request=self.get_request(test_link))
            response = url.get_response()
            url.close()

        print("OK")

    def test_get_response__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        if not self.is_memory_test():
            return

        for i in range(1, self.iteration_count):
            test_link = "https://www.youtube.com/watch?v=1234"
            url = MockUrl(request=self.get_request(test_link))
            response = url.get_response()
            url.close()

        print("OK")
