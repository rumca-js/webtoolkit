import traceback
from concurrent.futures import ThreadPoolExecutor

from ..response import PageResponseObject
from ..urllocation import UrlLocation
from ..pages import RssPage
from ..webtools import WebLogger
from .defaulturlhandler import DefaultCompoundChannelHandler
from .handlerhttppage import HttpPageHandler


class YouTubeHandler(DefaultCompoundChannelHandler):
    """
    Generic youtube domain handler
    """

    def __init__(self, url=None, request=None, url_builder=None):
        super().__init__(
            url=url,
            request=request,
            url_builder=url_builder,
        )

        if not self.is_handled_by():
            return

        if self.request:
            self.request.cookies = {}
            self.request.cookies["CONSENT"] = "YES+cb.20210328-17-p0.en+F+678"

    def is_handled_by(self):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()

        if (
            short_url.startswith("www.youtube.com")
            or short_url.startswith("youtube.com")
            or short_url.startswith("m.youtube.com")
        ):
            return True

        return False

    def get_language(self):
        """
        Social media platforms host very different videos in different locations
        Currently I have no means of identifying og:locale, or lang, it is commonly
        locale of platform, not contents
        """
        return None
