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
       "data" : {},
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


class UrlTest(FakeInternetTestCase):
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

    def test_get_hash(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response.get_hash())

    def test_get_body_hash(self):
        u = RemoteUrl("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response.body_hash)

    def test_get_feeds(self):
        u = RemoteUrl("https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")
        response = u.get_response()
        feeds = u.get_feeds()

        self.assertTrue(len(feeds) > 0)

