from datetime import datetime

from webtoolkit import UrlLocation, RemoteUrl
from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.fakeinternetcontents import webpage_with_real_rss_links


all_properties = [
   {
       "data" : {},
       "name" : "Properties",
   },
   {
       "data" : {},
       "name" : "Text",
   },
   {
       "data" : {
           "https://example.com" : {
               "status_code" : 200,
               "request" : {
                   "url": "https://example.com",
                   "crawler_name" : "Fake Properties Crawler2",
               },
               "text" : "<html></html"
           }
       },
       "name" : "Streams",
   },
   {
       "data" : {
           "crawler_name" : "Fake Properties Crawler1",
       },
       "name" : "Request",
   },
   {
       "data" : {
           "status_code" : 200,
           "request" : {
               "url": "https://example.com",
               "crawler_name" : "Fake Properties Crawler2",
           }
       },
       "name" : "Response",
   },
]


class RemoteUrlTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor__all_properties(self):
        u = RemoteUrl(all_properties=all_properties)

        response = u.get_response()

        self.assertTrue(response)
        self.assertEqual(response.get_status_code(), 200)
        self.assertTrue(response.request)
        self.assertEqual(response.request.crawler_name, "Fake Properties Crawler2")

    def test_get_response(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text)

    def test_get_properties__html(self):
        u = RemoteUrl("https://linkedin.com")
        properties = u.get_properties()

        self.assertTrue(properties)
        self.assertIn("title", properties)
        self.assertIn("description", properties)
        self.assertIn("link", properties)

    def test_get_social_properties(self):
        u = RemoteUrl("https://github.com/rumca-js/Django-link-archive")
        properties = u.get_social_properties()

        self.assertTrue(properties)
        self.assertIn("stars", properties)

    def test_get_text(self):
        u = RemoteUrl("https://google.com")
        text = u.get_text()

        self.assertTrue(text)

    def test_get_hash(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(u.get_hash())

        self.assertTrue(response.get_hash())

    def test_get_body_hash(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(u.get_body_hash())

        self.assertTrue(response.body_hash)

    def test_get_meta_hash(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        hash = u.get_meta_hash()

        self.assertTrue(hash)

    def test_get_feeds(self):
        u = RemoteUrl("https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")
        response = u.get_response()
        feeds = u.get_feeds()

        self.assertTrue(len(feeds) > 0)

    def get_from_properties__youtube_video(self):
        test_link = "https://www.youtube.com/watch?v=1234"
        url = BaseUrl(test_link)
        all_properties = url.get_properties(full=True)

        u = RemoteUrl(all_properties=all_properties)
        response = u.get_response()

        self.assertTrue(response)

    def get_from_properties__youtube_channel(self):
        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = BaseUrl(test_link)
        all_properties = url.get_properties(full=True)

        u = RemoteUrl(all_properties=all_properties)
        response = u.get_response()

        self.assertTrue(response)

    def get_from_properties__reddit(self):
        test_link = "https://www.reddit.com/r/searchengines/.rss"

        url = BaseUrl(test_link)
        all_properties = url.get_properties(full=True)

        u = RemoteUrl(all_properties=all_properties)
        response = u.get_response()

        self.assertTrue(response)
