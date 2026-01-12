from ..urllocation import UrlLocation
from .defaulturlhandler import DefaultUrlHandler
from .handlerhttppage import HttpPageHandler


class OdyseeVideoHandler(DefaultUrlHandler):
    def __init__(self, url=None, contents=None, request=None, url_builder=None):
        super().__init__(
            url, contents=contents, request=request, url_builder=url_builder
        )
        self.channel_code = None
        self.video_code = None
        self.url = self.input2url(url)

    def is_handled_by(self):
        if not self.url:
            return

        protocol_less = UrlLocation(self.url).get_protocolless()

        if protocol_less.startswith("odysee.com/@"):
            wh1 = protocol_less.find("@")
            wh2 = protocol_less.find("/", wh1 + 1)
            if wh2 >= 0:
                return True
        elif protocol_less.startswith("odysee.com/"):
            # syntax reserved for channel RSS
            # test_link = "https://odysee.com/$/rss/@samtime:0"
            if protocol_less.startswith("odysee.com/$"):
                return False
            return True

    def input2url(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        if protocol_less.startswith("odysee.com/@"):
            return self.handle_channel_video_input(url)
        elif protocol_less.startswith("odysee.com/"):
            return self.handle_video_input(url)

    def handle_channel_video_input(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        lines = protocol_less.split("/")
        if len(lines) < 3:
            return

        first = lines[0]  # odysee.com
        self.channel_code = lines[1]
        self.video_code = lines[2]
        wh = self.video_code.find("?")
        if wh >= 0:
            self.video_code = self.video_code[:wh]

        protocol_less = "/".join([first, self.channel_code, self.video_code])

        return "https://" + protocol_less

    def handle_video_input(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        lines = protocol_less.split("/")
        if len(lines) < 2:
            return url

        first = lines[0]  # odysee.com
        self.video_code = lines[1]

        protocol_less = "/".join([first, self.video_code])

        return "https://" + protocol_less

    def get_video_code(self):
        return self.video_code

    def get_channel_code(self):
        return self.channel_code

    def get_link_classic(self):
        if self.get_channel_code():
            return "https://odysee.com/{}/{}".format(
                self.get_channel_code(), self.get_video_code()
            )
        else:
            return "https://odysee.com/{}".format(self.get_video_code())

    def get_link_embed(self):
        return "https://odysee.com/$/embed/{0}".format(self.get_video_code())

    def get_feeds(self):
        from .handlerchannelodysee import OdyseeChannelHandler

        feeds = OdyseeChannelHandler(channel_code=self.channel_code).get_feeds()
        return feeds

    def get_language(self):
        """
        Social media platforms host very different videos in different locations
        Currently I have no means of identifying og:locale, or lang, it is commonly
        locale of platform, not contents
        """
        return None
