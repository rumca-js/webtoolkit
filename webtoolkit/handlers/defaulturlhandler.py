import copy

from ..utils.dateutils import DateUtils
from ..pages import DefaultContentPage
from ..request import PageRequestObject
from ..webconfig import WebLogger
from .handlerhttppage import HttpPageHandler


class DefaultUrlHandler(HttpPageHandler):
    """ """

    def __init__(self, url=None, contents=None, request=None, url_builder=None):
        self.code = None
        super().__init__(url=url, request=request, url_builder=url_builder)
        self.code = self.input2code(self.url)

    def get_page_url(self, url, crawler_name=None):
        """
        Obtains a custom, another URL using a crawler
        Necessary for more advanced handlers that in order to provide necessary data
        check multiple source of data.
        """
        if not url:
            return

        if self.request:
            request = copy.copy(self.request)
        else:
            request = PageRequestObject(url)

        request.url = url
        request.handler_type = HttpPageHandler
        request.crawler_type = None
        if crawler_name:
            request.crawler_name = crawler_name

        if self.url_builder:
            url = self.url_builder(
                url=url, request=request, url_builder=self.url_builder
            )
            return url

    def build_default_url(self, url, crawler_name=None):
        """
        TODO reneme get_page_url to build_http_url
        """
        if not url:
            return

        if self.request:
            request = copy.copy(self.request)
        else:
            request = PageRequestObject(url)

        request.url = url

        request.crawler_type = None
        if crawler_name:
            request.crawler_name = crawler_name

        if self.url_builder:
            url = self.url_builder(
                url=url, request=request, url_builder=self.url_builder
            )
            return url


class DefaultChannelHandler(DefaultUrlHandler):
    """
    Default handler for channels
    """

    pass


class DefaultRssChannelHandler(DefaultUrlHandler):
    def __init__(self, url=None, contents=None, request=None, url_builder=None):
        self.rss_url = None
        super().__init__(url=url, request=request, url_builder=url_builder)

    def get_channel_name(self):
        url = self.get_rss_url()
        if url:
            return url.get_title()

    def get_contents(self):
        """
        We obtain information about channel.
        We cannot use HTML page to obtain thumbnail - as web page asks to log in to view this
        """
        if self.dead:
            return

        if self.contents:
            return self.contents

        if self.response:
            return self.response.get_text()

        response = self.get_response()
        if response:
            return self.response.get_text()

    def get_response(self):
        if not self.code:
            return

        if self.response:
            return self.response

        if self.dead:
            return

        self.rss_url = self.get_rss_url()

        if self.rss_url:
            self.response = self.rss_url.get_response()
        else:
            WebLogger.error("Could not obtain RSS")

        return self.response

    def get_rss_url(self):
        #print("get_rss_url")
        if self.rss_url:
            return self.rss_url

        feeds = self.get_feeds()
        if not feeds or len(feeds) == 0:
            WebLogger.error(
                "Url:{} Cannot read YouTube channel feed URL".format(self.url)
            )
            return

        feed = feeds[0]
        if not feed:
            return

        self.rss_url = self.get_page_url(feed)
        if not self.rss_url:
            return

        self.rss_url.get_response()
        #print("get_rss_url DONE")
        return self.rss_url

    def get_entries(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_entries()
        else:
            return []

    def get_title(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_title()

    def get_description(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_description()

    def get_language(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_language()

    def get_thumbnail(self):
        rss_url = self.get_rss_url()
        if rss_url:
            thumbnail = rss_url.get_thumbnail()
            if thumbnail:
                return thumbnail

    def get_author(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_author()

    def get_album(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_album()

    def get_tags(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_tags()

