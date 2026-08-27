"""
Set of manual, real world tests
"""
import unittest
import gc

from webtoolkit import (
   BaseUrl,
   RemoteUrl,
   YouTubeChannelHandler,
   YouTubeVideoHandler,
   OdyseeChannelHandler,
   OdyseeVideoHandler,
   PageRequestObject,
   HttpPageHandler,
   CrawlerInterface,
   RequestsCrawler,
)
from webtoolkit.utils.memorychecker import MemoryChecker
from webtoolkit.webconfig import WebConfig


class TestMemoryBaseUrl(unittest.TestCase):
    def setUp(self):
        WebConfig.use_print_logging()

        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()
        self.ignore_memory = False
        self.num_iterations = 100

    def tearDown(self):
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertTrue(memory_increase < 40)

    def call_url(self, test_url):
        print("Running {} with BaseUrl".format(test_url))

        url = BaseUrl(url=test_url)
        response = None
        handler = None
        response = url.get_response()
        handler = url.get_handler()
        return response, handler, url

    def test_get_response__vanilla_google(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.google.com"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_get_response__reddit__channel(self):
        """
        """
        for i in range(1, self.num_iterations):
            test_url = "https://www.reddit.com/r/wizardposting"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_get_response__github(self):
        """
        """
        for i in range(1, self.num_iterations):
            test_url = "https://github.com/rumca-js/crawler-buddy"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_get_response__youtube_channel_by_id(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_get_social_data(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

            url = BaseUrl(url=test_url)
            response = None
            handler = None
            social = url.get_social_properties()

            url.close()
