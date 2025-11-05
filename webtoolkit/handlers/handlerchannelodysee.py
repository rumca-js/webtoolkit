from concurrent.futures import ThreadPoolExecutor

from ..urllocation import UrlLocation
from ..webtools import WebLogger
from .defaulturlhandler import DefaultCompoundChannelHandler
from .handlerhttppage import HttpPageHandler


class OdyseeChannelHandler(DefaultCompoundChannelHandler):

    def __init__(self, url=None, contents=None, request=None, url_builder=None):

        super().__init__(
            url,
            contents=contents,
            request=request,
            url_builder=url_builder,
        )

        if url:
            self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True
        elif short_url.startswith("odysee.com/$/rss"):
            return True

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        return "https://odysee.com/{}".format(code)

    def code2feed(self, code):
        return "https://odysee.com/$/rss/{}".format(code)

    def get_feeds(self):
        feeds = super().get_feeds()
        if self.code:
            feeds.append("https://odysee.com/$/rss/{}".format(self.code))

        return feeds

    def is_channel_name(self):
        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True

    def input2code(self, url):
        wh = url.find("odysee.com")
        if wh == -1:
            return None

        if url.find("https://odysee.com/$/rss/") >= 0:
            return self.input2code_feeds(url)
        if url.find("https://odysee.com/") >= 0:
            return self.input2code_channel(url)

    def input2code_channel(self, url):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()
        lines = short_url.split("/")
        if len(lines) < 2:
            return

        base = lines[0]  # odysee.com
        code = lines[1]

        wh = code.find("?")
        if wh >= 0:
            code = code[:wh]

        return code

    def input2code_feeds(self, url):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()
        lines = short_url.split("/")
        if len(lines) < 2:
            return

        base = lines[0]  # odysee.com
        dollar = lines[1]  # $
        rss = lines[2]  # rss
        code = lines[3]

        wh = code.find("?")
        if wh >= 0:
            code = code[:wh]

        return code
