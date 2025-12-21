"""
Set of manual, real world tests
"""
import requests
import unittest

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
from webtoolkit.webconfig import WebConfig


class TestBaseUrl(unittest.TestCase):
    def run_with_base_url(self, test_url):
        print("Running {} with BaseUrl".format(test_url))

        url = BaseUrl(url=test_url)
        response = url.get_response()
        handler = url.get_handler()

        self.assertTrue(handler.get_title())
        self.assertTrue(handler.get_hash())
        self.assertTrue(handler.get_body_hash())

        self.assertTrue(response is not None)
        self.assertTrue(response.is_valid())
        self.assertTrue(response.get_text())
        self.assertTrue(response.get_hash())
        self.assertTrue(response.get_body_hash())

        properties = url.get_social_properties()
        print(f"Social properties: {properties}")

        return response, handler

    def test_baseurl__vanilla_google(self):
        test_url = "https://www.google.com"
        response,handler = self.run_with_base_url(test_url)

        self.assertEqual(len(list(handler.get_entries())), 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        return response, handler

    def test_baseurl__youtube_video(self):
        test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
        response, handler = self.run_with_base_url(test_url)
        if handler:
            print("Title: {}".format(handler.get_title()))

        self.assertEqual(len(list(handler.get_entries())), 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        return response, handler

    def test_baseurl__youtube_channel_by_id(self):
        test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        response, handler = self.run_with_base_url(test_url)

        entries_len = len(list(handler.get_entries()))
        streams_len = len(list(handler.get_streams()))

        self.assertTrue(handler.get_title() == "Linus Tech Tips")
        self.assertTrue(handler.get_code())
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        self.assertTrue(response.is_valid())
        self.assertTrue(streams_len == 2)
        self.assertTrue(entries_len == 15)

        return response, handler

    def test_baseurl__youtube_channel_by_handle(self):
        test_url = "https://www.youtube.com/@LinusTechTips"
        response, handler = self.run_with_base_url(test_url)

        entries_len = len(list(handler.get_entries()))
        streams_len = len(list(handler.get_streams()))

        self.assertTrue(handler.get_title() == "Linus Tech Tips")
        self.assertTrue(handler.get_code())
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        self.assertTrue(response.is_valid())
        self.assertTrue(streams_len == 2)
        self.assertTrue(entries_len > 0)

        return response, handler

    def test_baseurl__odysee_channel(self):
        test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
        response, handler = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__odysee_video(self):
        test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"
        response, handler = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__github(self):
        test_url = "https://github.com/rumca-js/crawler-buddy"
        response, handler = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__reddit__channel(self):
        test_url = "https://www.reddit.com/r/wizardposting"
        response, handler = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__reddit__news(self):
        test_url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/"
        response, handler = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__remote_url(self):
        test_url = "https://www.google.com"

        url = BaseUrl(url=test_url)
        response = url.get_response()
        handler = url.get_handler()

        all_properties = url.get_all_properties()

        remote_url = RemoteUrl(all_properties=all_properties)
        response = remote_url.get_response()

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        self.assertTrue(response is not None)
        self.assertTrue(response.is_valid())
        self.assertTrue(response.get_text())
        self.assertTrue(response.get_hash())
        self.assertTrue(response.get_body_hash())

        self.assertTrue(remote_url.get_title())
        self.assertTrue(remote_url.get_hash())
        self.assertTrue(remote_url.get_body_hash())

        remote_responses = remote_url.get_responses()
        self.assertTrue(remote_responses)
        self.assertTrue(len(remote_responses) > 0)

    def test_baseurl__is_allowed(self):
        test_url = "https://www.youtube.com/watch?v=Vzgimftolys&pp=ygUPbGludXMgdGVjaCB0aXBz"

        url = BaseUrl(url=test_url)
        self.assertTrue(url.is_allowed())


"""
class TestBaseUrl(unittest.TestCase):

    def run_with_handler(self, test_url, handler):
        print("Running {} with BaseUrl".format(test_url))

        url = BaseUrl(url=test_url)
        response = url.get_response()
        handler = url.get_handler()

        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        self.assertTrue(response is not None)
        self.assertTrue(response.is_valid())
        self.assertTrue(response.get_text())
        self.assertTrue(response.get_title())
        self.assertTrue(response.get_hash())
        self.assertTrue(response.get_body_hash())

        properties = url.get_social_properties()
        print(f"Social properties: {properties}")

        return response, handler

    def test_handler_vanilla_google(self):
        test_url = "https://www.google.com"
        response, handler = run_with_handler(test_url, HttpPageHandler)
        return response, handler

    def test_handler_youtube_channel_by_rss(self):
        test_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    def test_handler_youtube_channel_by_channel(self):
        test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    def test_handler_youtube_channel_by_handle(self):
        test_url = "https://www.youtube.com/@LinusTechTips"
        response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    def test_handler_youtube_video(self):
        test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
        return run_with_handler(test_url, YouTubeVideoHandler)

    def test_handler_odysee_channel(self):
        test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
        response, handler = run_with_handler(test_url, OdyseeChannelHandler)

    def test_handler_odysee_video(self):
        test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"

        return run_with_handler(test_url, OdyseeVideoHandler)
"""
