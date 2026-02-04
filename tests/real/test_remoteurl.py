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
   json_encode_field,
)
from webtoolkit.webconfig import WebConfig


class TestRemoteUrl(unittest.TestCase):
    def run_with_remote_url(self, test_url):
        print("Running {} with RemoteUrl".format(test_url))

        location = "http://192.168.0.200:3000"

        url = RemoteUrl(url=test_url, remote_server_location=location)
        response = url.get_response()

        self.assertTrue(response is not None)
        self.assertTrue(response.is_valid())
        self.assertTrue(response.get_text())

        hash = response.get_hash()
        body_hash = response.get_body_hash()
        self.assertTrue(hash)
        self.assertTrue(body_hash)

        print("Hash {}".format(json_encode_field(hash)))
        print("Body hash {}".format(json_encode_field(body_hash)))

        return response, url

    def test_vanilla_google(self):
        test_url = "https://www.google.com"
        response, url = self.run_with_remote_url(test_url)

        self.assertEqual(response.request.crawler_name, "CurlCffiCrawler")

        properties = url.get_social_properties()
        self.assertTrue(len(properties) > 0)

        return response
