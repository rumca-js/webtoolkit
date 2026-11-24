"""
Integration tests for RemoteUrl against a live remote crawler server.
"""

import os
import unittest

from webtoolkit import RemoteUrl, SocialData, json_encode_field
from webtoolkit.remoteserver import RemoteServer
from webtoolkit.statuses import HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS
from webtoolkit.webconfig import WebConfig

DEFAULT_REMOTE_SERVER = (
    os.environ.get("CRAWLER_BUDDY_URL")
    or os.environ.get("REMOTE_SERVER_LOCATION")
    or RemoteServer.get_remote_server_location()
    or "http://127.0.0.1:3000"
)


class TestRemoteUrl(unittest.TestCase):
    def setUp(self):
        WebConfig.use_print_logging()
        self.server_location = DEFAULT_REMOTE_SERVER

    def run_with_remote_url(self, test_url):
        print(f"Running {test_url} with RemoteUrl ({self.server_location})")

        url = RemoteUrl(url=test_url, remote_server_location=self.server_location)
        response = url.get_response()

        if response is None:
            self.skipTest(
                f"Remote crawler at {self.server_location} did not return a response (unreachable or connection error)"
            )

        if response.status_code == HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS:
            self.skipTest(
                f"Remote crawler at {self.server_location} reported status 615 (server too many requests/overloaded)"
            )

        self.assertIsNotNone(response)
        self.assertTrue(response.is_valid())
        self.assertTrue(response.get_text())

        response_hash = response.get_hash()
        body_hash = response.get_body_hash()
        self.assertTrue(response_hash)
        self.assertTrue(body_hash)

        print(f"Hash: {json_encode_field(response_hash)}")
        print(f"Body hash: {json_encode_field(body_hash)}")

        return response, url

    def test_vanilla_google(self):
        test_url = "https://www.google.com"
        response, url = self.run_with_remote_url(test_url)

        self.assertEqual(response.status_code, 200)

        if response.request and response.request.crawler_name:
            self.assertEqual(response.request.crawler_name, "CurlCffiCrawler")

        properties = url.get_properties()
        self.assertIsInstance(properties, dict)

        social_properties = url.get_social_properties()
        self.assertIsInstance(social_properties, SocialData)

        links = url.get_content_links()
        self.assertIsInstance(links, (list, set))
        self.assertTrue(len(links) > 0)

    def test_github_repo(self):
        test_url = "https://github.com/codecrafters-io/build-your-own-x"
        response, url = self.run_with_remote_url(test_url)

        self.assertEqual(response.status_code, 200)

        properties = url.get_properties()
        self.assertIsInstance(properties, dict)
        self.assertTrue(len(properties) > 0)

        title = url.get_title()
        self.assertTrue(title)
        print(f"GitHub title: {title}")

        description = url.get_description()
        print(f"GitHub description: {description}")

        canonical = url.get_canonical_link()
        print(f"GitHub canonical: {canonical}")

        social = url.get_social_properties()
        self.assertIsInstance(social, SocialData)
        self.assertIsNotNone(social.stars)
        self.assertGreater(social.stars, 0)
        print(f"GitHub stars: {social.stars}")
        print(f"GitHub sources: {social.sources}")

        social_data = url.get_social_data()
        self.assertIsInstance(social_data, SocialData)

        feeds = url.get_feeds()
        self.assertIsInstance(feeds, (list, set))
        print(f"GitHub feeds: {feeds}")

    def test_youtube_video(self):
        test_url = "https://www.youtube.com/watch?v=tLPZmPaHme0"
        response, url = self.run_with_remote_url(test_url)

        self.assertEqual(response.status_code, 200)

        properties = url.get_properties()
        self.assertIsInstance(properties, dict)
        self.assertTrue(len(properties) > 0)

        title = url.get_title()
        self.assertTrue(title)
        print(f"YouTube title: {title}")

        canonical = url.get_canonical_link()
        self.assertEqual(canonical, test_url)
        print(f"YouTube canonical: {canonical}")

        social = url.get_social_properties()
        self.assertIsInstance(social, SocialData)
        self.assertIsNotNone(social.view_count)
        self.assertGreater(social.view_count, 0)
        self.assertIsNotNone(social.thumbs_up)
        self.assertGreater(social.thumbs_up, 0)
        print(f"YouTube views: {social.view_count}")
        print(f"YouTube thumbs up: {social.thumbs_up}")
        print(f"YouTube thumbs down: {social.thumbs_down}")

        social_data = url.get_social_data()
        self.assertIsInstance(social_data, SocialData)

    def test_youtube_channel(self):
        test_url = "https://www.youtube.com/channel/UCCHcEUksSVKsRDH86j77Ntg"
        response, url = self.run_with_remote_url(test_url)

        self.assertEqual(response.status_code, 200)

        properties = url.get_properties()
        self.assertIsInstance(properties, dict)
        self.assertTrue(len(properties) > 0)

        title = url.get_title()
        self.assertTrue(title)
        print(f"YouTube channel title: {title}")

        canonical = url.get_canonical_link()
        self.assertEqual(canonical, test_url)
        print(f"YouTube channel canonical: {canonical}")

        feeds = url.get_feeds()
        self.assertIsInstance(feeds, (list, set))
        self.assertTrue(len(feeds) > 0)
        print(f"YouTube channel feeds: {feeds}")

        social = url.get_social_properties()
        self.assertIsInstance(social, SocialData)
        self.assertIsNotNone(social.followers_count)
        self.assertGreater(social.followers_count, 0)
        print(f"YouTube channel subscribers: {social.followers_count}")

        social_data = url.get_social_data()
        self.assertIsInstance(social_data, SocialData)


if __name__ == "__main__":
    unittest.main()
