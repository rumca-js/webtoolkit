import traceback
from concurrent.futures import ThreadPoolExecutor

from ..urllocation import UrlLocation
from ..webtools import WebLogger
from .defaulturlhandler import DefaultCompoundChannelHandler


class YouTubeChannelHandler(DefaultCompoundChannelHandler):
    """
    Natively since we inherit RssPage, the contents should be RssPage
    """

    def __init__(self, url=None, request=None, url_builder=None):
        self.social_data = {}
        self.user_name = None

        super().__init__(
            url=url,
            request=request,
            url_builder=url_builder,
        )

        if not self.is_handled_by():
            return

    def is_handled_by(self):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()

        if (
            short_url.startswith("www.youtube.com/channel")
            or short_url.startswith("youtube.com/channel")
            or short_url.startswith("m.youtube.com/channel")
        ):
            return True
        if self.is_feed_url(self.url):
            return True
        if self.is_channel_name(self.url):
            return True

        return False

    def is_channel_name(self, url) -> bool:
        """
        For channel name it is more difficult to obtain channel code.
        """
        if not url:
            return False

        short_url = UrlLocation(url).get_protocolless()

        if (
            short_url.startswith("www.youtube.com/@")
            or short_url.startswith("youtube.com/@")
            or short_url.startswith("m.youtube.com/@")
            or short_url.startswith("www.youtube.com/user")
            or short_url.startswith("youtube.com/user")
            or short_url.startswith("m.youtube.com/user")
            or short_url.startswith("www.youtube.com/c/")
            or short_url.startswith("youtube.com/c/")
            or short_url.startswith("m.youtube.com/c/")
        ):
            return True
        return False

    def is_feed_url(self, url) -> bool:
        if not url:
            return False

        short_url = UrlLocation(url).get_protocolless()
        if (
            short_url.startswith("www.youtube.com/feeds")
            or short_url.startswith("youtube.com/feeds")
            or short_url.startswith("m.youtube.com/feeds")
        ):
            return True
        return False

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        if code:
            return "https://www.youtube.com/channel/{}".format(code)

    def code2feed(self, code):
        return "https://www.youtube.com/feeds/videos.xml?channel_id={}".format(code)

    def get_feeds(self):
        """
        Super class implementation may provide us feeds, start with that
        """
        if self.code is None:
            self.update_code()

        feeds = set(super().get_feeds())
        if self.code:
            feeds.add(self.code2feed(self.code))

        return list(feeds)

    def update_code(self):
        feeds = set(super().get_feeds())

        for feed in feeds:
            handler = YouTubeChannelHandler(url=feed)
            code = handler.get_code()
            if not self.code and code:
                self.code = code

    def input2code(self, url):
        wh = url.find("youtube.com")
        if wh == -1:
            return

        if self.is_channel_name(url):
            return
        if url.find("/channel/") >= 0:
            return self.input2code_channel(url)
        if url.find("/feeds/") >= 0:
            return self.input2code_feeds(url)

    def input2code_handle(self, url):
        page_handler = self.get_page_url(url)
        if not page_handler:
            return

        response = page_handler.get_response()
        if not response:
            return

        props = page_handler.get_properties()
        if not props:
            return

        if "feeds" in props:
            if len(props["feeds"]) > 0:
                feed = props["feeds"][0]
                return self.input2code(feed)

    def intpu2handlename(self, url):
        wh = url.find("?")
        if wh >= 0:
            url = url[:wh]

        wh1 = url.find("youtube.com/user")
        if wh1 >= 0:
            start = wh1 + len("youtube.com/user") + 1
            wh2 = url.find("/", start + 1)
            if wh2 == -1:
                return url[start - 1 :]
            else:
                return url[start - 1 : wh2]

        wh1 = url.find("youtube.com/@")
        if wh1 >= 0:
            start = wh1 + len("youtube.com/@") + 1
            wh2 = url.find("/", start + 1)
            if wh2 == -1:
                return url[start - 1 :]
            else:
                return url[start - 1 : wh2]

    def input2code_channel(self, url):
        wh = url.rfind("/")
        return url[wh + 1 :]

    def input2code_feeds(self, url):
        wh = url.find("=")
        if wh >= 0:
            return url[wh + 1 :]

    def get_channel_code(self):
        return self.code

    def get_channel_url(self):
        if self.code:
            return self.code2url(self.code)

    def get_canonical_url(self):
        if self.url.find("feeds") >= 0:
            return self.url
        else:
            return self.get_channel_url()

    def get_responses(self):
        code_was_none = False
        if self.code is None:
            code_was_none = True

        responses = super().get_responses()

        if code_was_none:
            # if it was handle, then at first time obtain channel ID
            # call second time to obtain rss feeds now
            self.update_code()
            if self.code:
                feed = self.code2feed(self.code)
                url = self.get_page_url(feed)
                self.channel_sources_urls[url.url] = url
                responses.append(url.get_response())

        return responses

    def get_language(self):
        """
        Social media platforms host very different videos in different locations
        Currently I have no means of identifying og:locale, or lang, it is commonly
        locale of platform, not contents
        """
        return None
