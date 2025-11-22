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
)

from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockRequestCounter, MockCrawler, MockUrl


class BaseUrlTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def get_request(self, url):
        request = PageRequestObject(url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url)
        return request

    def test_get_cleaned_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://my-server:8185/view/somethingsomething/"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))
        link = url.request.url

        self.assertEqual(link, "https://my-server:8185/view/somethingsomething")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__space(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = " https://my-server:8185/view/somethingsomething/"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))
        link = url.request.url

        self.assertEqual(link, "https://my-server:8185/view/somethingsomething")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_google_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.google.com/url?q=https://forum.ddopl.com/&sa=Udupa"
        url = MockUrl(request=self.get_request(test_link))
        cleaned_link = url.request.url

        self.assertEqual(cleaned_link, "https://forum.ddopl.com")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_google_link2(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://worldofwarcraft.blizzard.com/&ved=2ahUKEwjtx56Pn5WFAxU2DhAIHYR1CckQFnoECCkQAQ&usg=AOvVaw1pDkx5K7B5loKccvg_079-"

        url = MockUrl(request=self.get_request(test_link))
        link = url.request.url

        self.assertEqual(link, "https://worldofwarcraft.blizzard.com")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_youtube_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810"

        url = MockUrl(request=self.get_request(test_link))
        link = url.request.url

        self.assertEqual(link, "https://corridordigital.com")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.YouTube.com/Test"
        url = MockUrl(request=self.get_request(test_link))
        cleaned_link = url.request.url

        self.assertEqual(cleaned_link, "https://www.youtube.com/Test")

        test_link = "https://www.YouTube.com/Test/"
        url = MockUrl(test_link)
        link = url.request.url

        self.assertEqual(cleaned_link, "https://www.youtube.com/Test")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__https_html_page(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__http_html_page(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "http://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        self.assertEqual(type(url.get_handler()), RedditUrlHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), RssPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__ftp_page(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "ftp://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))

        expected_error = False
        try:
            url.get_response()
        except NotImplementedError as E:
            expected_error = True

        self.assertTrue(expected_error)
        # self.assertEqual(url.get_handler(), None)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__rss_page(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        url = MockUrl("https://www.codeproject.com/WebServices/NewsRSS.aspx")

        handler = url.get_handler()

        self.assertTrue(type(handler), HttpPageHandler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        handler = url.get_handler()

        self.assertTrue(type(handler), Url.youtube_channel_handler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        test_link = "https://www.youtube.com/watch?v=1234"
        url = MockUrl(request=self.get_request(test_link))

        handler = url.get_handler()

        self.assertTrue(type(handler), Url.youtube_video_handler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__https_html_page__norequest(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        self.assertEqual(url.get_handler().p, None)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_type__html_page(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://multiple-favicons.com/page.html"

        handler = MockUrl(test_link).get_type()

        # call tested function
        self.assertEqual(type(handler), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__rss_page(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        handler = url.get_type()

        self.assertTrue(type(handler), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        handler = url.get_type()

        self.assertTrue(type(handler), YouTubeChannelHandler)

    def test_get_handler__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        # call tested function
        handler = MockUrl(test_link).get_type()

        self.assertTrue(type(handler), YouTubeVideoHandler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_properties__rss__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_channel__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        # +1 html +1 RSS
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_properties__youtube_video__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        # +1 for HTML
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_video__date_published(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=date_published"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        response = url.get_response()
        properties = url.get_properties()

        self.assertIn("title", properties)
        self.assertIn("link", properties)
        self.assertIn("date_published", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)
        self.assertTrue(properties["date_published"])

        # +1 for HTML
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__html__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-two-links.com"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__html__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-two-links.com"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()
        self.assertTrue(len(all_properties) > 0)

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__rss__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()
        self.assertTrue(len(all_properties) > 0)

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)
        self.assertIn("feeds", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        entries_section = RemoteServer.read_properties_section("Entries", all_properties)
        self.assertTrue(entries_section)
        self.assertTrue(len(entries_section) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_channel__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()
        self.assertTrue(len(all_properties) > 0)

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)
        self.assertIn("feeds", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        entries_section = RemoteServer.read_properties_section("Entries", all_properties)
        self.assertTrue(entries_section)
        self.assertTrue(len(entries_section) > 0)

        # +1 HTML +1 RSS
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_properties__odysee_channel__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://odysee.com/$/rss/@DistroTube:2"

        # call tested function
        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        all_properties = url.get_all_properties()

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)
        self.assertIn("feeds", properties_section)

        #self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        entries_section = RemoteServer.read_properties_section("Entries", all_properties)
        self.assertTrue(entries_section)
        self.assertTrue(len(entries_section) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_properties__youtube_video__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        # +1 for yt dlp +1 for return dislike
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__image_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://binary.jpg.com"

        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        streams_section = RemoteServer.read_properties_section("Streams", all_properties)
        self.assertTrue(streams_section)
        self.assertTrue(len(streams_section) > 0)

        response_section = RemoteServer.read_properties_section("Response", all_properties)

        self.assertEqual(response_section["Content-Type"], "image/jpg")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__audio_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://audio.jpg.com"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()
        # call tested function
        all_properties = url.get_all_properties()

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        streams_section = RemoteServer.read_properties_section("Streams", all_properties)
        self.assertTrue(streams_section)
        self.assertTrue(len(streams_section) > 0)

        response_section = RemoteServer.read_properties_section("Response", all_properties)

        self.assertEqual(response_section["Content-Type"], "audio/midi")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__video_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://video.jpg.com"

        url = MockUrl(request=self.get_request(test_link))

        url.get_response()

        # call tested function
        all_properties = url.get_all_properties()
        self.assertTrue(len(all_properties) > 0)

        properties_section = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertTrue(properties_section)

        self.assertIn("title", properties_section)
        self.assertIn("link", properties_section)

        self.assertEqual(properties_section["link"], test_link)
        self.assertEqual(properties_section["link_request"], test_link)

        streams_section = RemoteServer.read_properties_section("Streams", all_properties)
        self.assertTrue(streams_section)
        self.assertTrue(len(streams_section) > 0)

        response_section = RemoteServer.read_properties_section("Response", all_properties)

        self.assertEqual(response_section["Content-Type"], "video/mp4")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents__pass(self):
        test_link = "https://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        contents = url.get_contents()
        self.assertTrue(contents != None)

    def test_get_contents__fails(self):
        MockRequestCounter.reset()

        test_link = "https://page-with-http-status-500.com"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        contents = url.get_contents()
        self.assertFalse(url.is_valid())

        # 1 for requests +1 for next
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

        self.assertEqual(len(MockRequestCounter.request_history), 1)

        self.assertEqual(MockRequestCounter.request_history[0]["url"], "https://page-with-http-status-500.com")

    def test_is_valid__html(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://multiple-favicons.com/page.html"
        url = MockUrl(request=self.get_request(test_link))

        self.assertEqual(url.get_handler().p, None)

        url.get_response()

        self.assertEqual(type(url.get_handler().p), HtmlPage)

        # call tested function
        self.assertTrue(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_is_valid__image(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://binary.jpg.com"

        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        self.assertTrue(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_is_valid__false_response_invalid(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-http-status-500.com"
        url = MockUrl(request=self.get_request(test_link))

        self.assertEqual(type(url.get_handler()), HttpPageHandler)

        self.assertEqual(url.get_handler().p, None)
        url.get_response()

        self.assertEqual(type(url.get_handler().p), HtmlPage)

        # call tested function
        self.assertFalse(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_last_modified(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-last-modified-header.com"
        url = MockUrl(request=self.get_request(test_link))

        response = url.get_response()

        self.assertTrue(response)

        last_modified = response.get_last_modified()
        self.assertTrue(last_modified)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_find_rss_url__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))

        result = url.find_rss_url()
        self.assertEqual(result.url, url.get_feeds()[0])

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_link_result = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__odysee(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://odysee.com/@samtime:1?test"
        test_link_result = "https://odysee.com/$/rss/@samtime:1"
        url = MockUrl(request=self.get_request(test_link))

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__rss(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        feeds = url.get_feeds()
        self.assertIn(test_link, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_feeds__opml(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://opml-file-example.com/ompl.xml"
        test_link_result = "https://www.opmllink1.com"

        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertNotIn(test_link, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_find_rss_url__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))

        result = url.find_rss_url()
        self.assertEqual(
            result.url,
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw",
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_find_rss_url__odysee(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://odysee.com/@samtime:1?test"
        url = MockUrl(request=self.get_request(test_link))

        result = url.find_rss_url()
        self.assertEqual(result.url, "https://odysee.com/$/rss/@samtime:1")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_find_rss_url__rss(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        result = url.find_rss_url()
        self.assertEqual(result, url)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_hash__html(self):
        MockRequestCounter.mock_page_requests = 0

        test_link ="https://linkedin.com"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_hash__rss(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_hash__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_hash()

        self.assertTrue(hash)

    def test_get_hash__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_body_hash__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_body_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_body_hash__html(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://linkedin.com"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_body_hash()

        self.assertTrue(hash)

        main_hash = url.get_hash()

        self.assertTrue(hash != main_hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_body_hash__rss(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_body_hash()

        self.assertTrue(hash)

        main_hash = url.get_hash()

        self.assertTrue(hash != main_hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_meta_hash__rss(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        hash = url.get_meta_hash()

        self.assertTrue(hash)

        main_hash = url.get_hash()

        self.assertTrue(hash != main_hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__html__canonical__norequest(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-canonical-link.com"
        test_canonical_link = "https://www.page-with-canonical-link.com"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 2)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertNotIn("link_canonical", urls)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__html__canonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-canonical-link.com"
        test_canonical_link = "https://www.page-with-canonical-link.com"

        url = MockUrl(request=self.get_request(test_link))
        url.get_response()

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/searchengines/.rss"
        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 2)
        self.assertEqual(urls["link"], "https://www.reddit.com/r/searchengines/.rss")
        self.assertEqual(urls["link_request"], "https://www.reddit.com/r/searchengines/.rss")
        self.assertNotIn("link_canonical", urls)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__stupid_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 2)
        self.assertEqual(urls["link"], "https://corridordigital.com")
        self.assertEqual(urls["link_request"], "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810")
        self.assertNotIn("link_canonical", urls)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_rss_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_channel_id(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_channel_id_non_canonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_canonical_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_video__noncanonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://m.youtube.com/watch?v=1234"
        test_canonical_link = "https://www.youtube.com/watch?v=1234"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_social_properties__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://m.youtube.com/watch?v=1234"

        url = MockUrl(request=self.get_request(test_link))

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("view_count", properties)
        self.assertTrue(properties["view_count"])
        self.assertIn("thumbs_up", properties)
        self.assertTrue(properties["thumbs_up"])
        self.assertIn("thumbs_down", properties)
        self.assertTrue(properties["thumbs_down"])

        # return dislike + youtube json
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__github(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://github.com/rumca-js?tab=repositories"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("stars", properties)
        self.assertTrue(properties["stars"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        properties = url.get_social_properties()

        self.assertTrue(properties)
        self.assertIn("upvote_ratio", properties)
        self.assertTrue(properties["upvote_ratio"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__html(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://linkedin.com/watch?v=1234"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("view_count", properties)
        self.assertIn("thumbs_up", properties)
        self.assertIn("thumbs_down", properties)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_response_to_data(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))

        # call tested function
        response = url.get_response()

        data = url.response_to_data(response)
        self.assertTrue(data)
        self.assertIn("is_valid", data)

    def test_is_allowed(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = MockUrl(request=self.get_request(test_link))
        self.assertFalse(url.is_allowed())
