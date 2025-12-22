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

        return response, handler, url

    def test_baseurl__vanilla_google(self):
        test_url = "https://www.google.com"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "HttpPageHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())

        self.assertEqual(len(list(handler.get_entries())), 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

        return response, handler

    def test_baseurl__youtube_video(self):
        test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "YouTubeVideoHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())
        self.assertEqual(len(list(handler.get_entries())), 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__youtube_channel_by_id(self):
        test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertEqual(handler.get_title(), "Linus Tech Tips")
        self.assertTrue(handler.get_code())
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        self.assertTrue(response.is_valid())

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__youtube_channel_by_handle(self):
        test_url = "https://www.youtube.com/@LinusTechTips"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertEqual(handler.get_title(), "Linus Tech Tips")
        self.assertTrue(handler.get_code())
        self.assertEqual(len(handler.get_feeds()), 1)
        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertEqual(len(list(handler.get_streams())), 2)

        self.assertTrue(response.is_valid())

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__odysee_channel(self):
        test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "OdyseeChannelHandler")
        self.assertTrue(len(list(handler.get_entries())) > 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__odysee_video(self):
        test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "OdyseeVideoHandler")
        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__github(self):
        test_url = "https://github.com/rumca-js/crawler-buddy"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "GitHubUrlHandler")
        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__reddit__channel(self):
        test_url = "https://www.reddit.com/r/wizardposting"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertEqual(handler.__class__.__name__, "RedditUrlHandler")
        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__reddit__post(self):
        test_url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/"
        response, handler, url = self.run_with_base_url(test_url)

        self.assertTrue(len(list(handler.get_entries())) == 0)
        self.assertTrue(len(list(handler.get_streams())) > 0)

    def test_baseurl__social_properties__reddit__channel(self):
        test_url = "https://www.reddit.com/r/wizardposting"

        response, handler, url = self.run_with_base_url(test_url)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

    def test_baseurl__social_properties__reddit__post(self):
        test_url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/"

        response, handler, url = self.run_with_base_url(test_url)

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

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
