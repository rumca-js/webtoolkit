from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
   YouTubeVideoHandler,
   YouTubeChannelHandler,
)

from webtoolkit.tests.fakeinternet import (
   FakeInternetTestCase, MockRequestCounter
)
from webtoolkit.tests.mocks import MockUrl


class YouTubeVideoHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=123"

        # call tested function
        handler = YouTubeVideoHandler(test_link, url_builder=MockUrl)

        self.assertEqual(handler.url, test_link)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_handled_by_video(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?v=1234")
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by_short(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/shorts/1234")
        self.assertTrue(handler.is_handled_by())

    def test_get_vide_code__video(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?v=1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_vide_code__short(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/shorts/1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_vide_code__watch_more_args(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?app=desktop&v=nkll0StZJLA&t=34s")
        self.assertEqual(handler.get_video_code(), "nkll0StZJLA")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__with_time(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler(
            "https://www.youtube.com/watch?v=uN_ab1GTXvY&t=50s"
        )
        self.assertEqual(handler.get_video_code(), "uN_ab1GTXvY")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__with_time_first(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler(
            "https://www.youtube.com/watch?t=50s&v=uN_ab1GTXvY"
        )
        self.assertEqual(handler.get_video_code(), "uN_ab1GTXvY")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://youtu.be/1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__youtube_time(self):
        handler = YouTubeVideoHandler("https://www.youtu.be/1234?t=50")
        self.assertEqual(handler.get_video_code(), "1234")

    def test_code2url(self):
        MockRequestCounter.mock_page_requests = 0

        self.assertEqual(
            YouTubeVideoHandler("1234").code2url("1234"),
            "https://www.youtube.com/watch?v=1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_link_embed(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeVideoHandler(test_link, url_builder=MockUrl)

        # call tested function
        link_embed = handler.get_link_embed()
        self.assertEqual(link_embed, "https://www.youtube.com/embed/123")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeVideoHandler(test_link, request=request, url_builder=MockUrl)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_hash(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeVideoHandler(test_link, request=request, url_builder=MockUrl)

        # call tested function
        hash = handler.get_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_body_hash(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeVideoHandler(test_link, request=request, url_builder=MockUrl)

        # call tested function
        hash = handler.get_body_hash()

        self.assertTrue(hash)

    def test_get_contents(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeVideoHandler(test_link, request=request,url_builder=MockUrl)

        # call tested function
        contents = handler.get_contents()

        self.assertTrue(contents)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeVideoHandler(test_link, request=request, url_builder=MockUrl)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_data__valid(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeVideoHandler(test_link, url_builder=MockUrl)
        handler.get_response()

        # call tested function
        social_data = handler.get_social_data()

        self.assertFalse(social_data is None)

        self.assertTrue(social_data["thumbs_up"])
        self.assertTrue(social_data["thumbs_down"])
        self.assertTrue(social_data["view_count"])
        self.assertTrue(social_data["rating"])
        self.assertTrue(social_data["upvote_ratio"])
        self.assertTrue(social_data["upvote_diff"])
        self.assertTrue(social_data["upvote_view_ratio"])
        self.assertFalse(social_data["stars"])
        self.assertFalse(social_data["followers_count"])

    def test_get_social_data__none(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=666"

        handler = YouTubeVideoHandler(test_link, url_builder=MockUrl)
        # call tested function
        social_data = handler.get_social_data()

        self.assertFalse(social_data is None)

        self.assertFalse(social_data["thumbs_up"])
        self.assertFalse(social_data["thumbs_down"])
        self.assertFalse(social_data["view_count"])
        self.assertFalse(social_data["rating"])
        self.assertFalse(social_data["upvote_ratio"])
        self.assertFalse(social_data["upvote_diff"])
        self.assertFalse(social_data["upvote_view_ratio"])
        self.assertFalse(social_data["stars"])
        self.assertFalse(social_data["followers_count"])



class YouTubeChannelHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor__rss(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
            url_builder=MockUrl
        )

        self.assertEqual(
            handler.get_feeds()[0],
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertEqual(handler.url, test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__user(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/user/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertEqual(handler.url, test_link)

        # +1 - obtains channel code from HTML
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_handled_by__channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__user(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/user/1234"
        # call tested function
        handler = YouTubeChannelHandler(url=test_link, url_builder=MockUrl)
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__a(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/@1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__feed(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"

        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertTrue(handler.is_handled_by())

    def test_source_input2code_channel(self):
        MockRequestCounter.mock_page_requests = 0
        self.assertEqual(
            YouTubeChannelHandler(
                "https://www.youtube.com/channel/1234"
            ).get_channel_code(),
            "1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_source_input2code_feed(self):
        MockRequestCounter.mock_page_requests = 0

        self.assertEqual(
            YouTubeChannelHandler(
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234"
            ).get_channel_code(),
            "1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_source_code2feed(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=1234"

        handler = YouTubeChannelHandler(test_link)

        self.assertIn(test_link, handler.get_feeds())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_channel_url(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        )

        # call tested function
        channel_name = handler.get_channel_url()

        self.assertEqual(
            channel_name,
            "https://www.youtube.com/channel/SAMTIMESAMTIMESAMTIMESAM",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            url = test_link,
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_hash(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        hash = handler.get_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_body_hash(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        hash = handler.get_body_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_contents(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        contents = handler.get_contents()

        self.assertTrue(contents)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_feeds__from_rss(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"

        handler = YouTubeChannelHandler(
            url = test_link
        )

        # call tested function
        feeds = handler.get_feeds()

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0], "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__from_channel(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/channel/SAMTIMESAMTIMESAMTIMESAM"
        )

        # call tested function
        feeds = handler.get_feeds()

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0], "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_thumbnail(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=MockUrl)
        self.assertEqual(handler.url, test_link)

        handler.get_response()

        thumbnail = handler.get_thumbnail()

        self.assertTrue(thumbnail)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_entries(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            url = test_link,
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        response = handler.get_response()
        entries = handler.get_entries()

        self.assertTrue(len(entries) > 0)

    def test_get_streams(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        request = MockUrl(test_link).get_init_request()

        handler = YouTubeChannelHandler(
            url = test_link,
            request=request,
            url_builder=MockUrl
        )

        # call tested function
        response = handler.get_response()
        streams = handler.get_streams()

        self.assertTrue(len(streams) > 0)
