from urllib.parse import urlparse
from urllib.parse import parse_qs

from ..utils.dateutils import DateUtils
from ..contentinterface import ContentInterface
from ..response import PageResponseObject
from ..urllocation import UrlLocation
from ..pages import HtmlPage, YouTubeVideoJson, ReturnDislikeJson
from ..webtools import WebLogger
from .defaulturlhandler import DefaultUrlHandler,DefaultCompoundChannelHandler


class YouTubeVideoHandler(DefaultCompoundChannelHandler):
    def __init__(self, url=None, contents=None, request=None, url_builder=None):
        super().__init__(
            url=url,
            contents=contents,
            request=request,
            url_builder=url_builder,
        )

        if not self.is_handled_by():
            return

        if request:
            request.cookies = {}
            request.cookies["CONSENT"] = "YES+cb.20210328-17-p0.en+F+678"

        self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        protocol_less = UrlLocation(self.url).get_protocolless()

        return (
            self.is_handled_by_watch(protocol_less)
            or self.is_handled_by_shorts(protocol_less)
            or self.is_handled_by_be_domain(protocol_less)
        )

    def is_handled_by_watch(self, protocol_less):
        return (
            protocol_less.startswith("www.youtube.com/watch")
            or protocol_less.startswith("youtube.com/watch")
            or protocol_less.startswith("m.youtube.com/watch")
        )

    def get_canonical_url(self):
        return self.code2url(self.code)

    def is_handled_by_shorts(self, protocol_less):
        return (
            protocol_less.startswith("www.youtube.com/shorts")
            or protocol_less.startswith("youtube.com/shorts")
            or protocol_less.startswith("m.youtube.com/shorts")
        )

    def is_handled_by_be_domain(self, protocol_less):
        return protocol_less.startswith("youtu.be/") and len(protocol_less) > len(
            "youtu.be/"
        )

    def get_video_code(self):
        return self.input2code(self.url)

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        if code:
            return "https://www.youtube.com/watch?v={0}".format(code)

    def input2code(self, url):
        if not url:
            return

        if url.find("watch") >= 0 and url.find("v=") >= 0:
            return YouTubeVideoHandler.input2code_standard(url)

        if url.find("shorts") >= 0:
            return YouTubeVideoHandler.input2code_shorts(url)

        if url.find("youtu.be") >= 0:
            return YouTubeVideoHandler.input2code_youtu_be(url)

    def input2code_youtu_be(url):
        wh = url.find("youtu.be")

        wh_question = url.find("?", wh)
        if wh_question >= 0:
            video_code = url[wh + 9 : wh_question]
        else:
            video_code = url[wh + 9 :]

        return video_code

    def input2code_shorts(url):
        wh = url.find("shorts")

        wh_question = url.find("?", wh)
        if wh_question >= 0:
            video_code = url[wh + 7 : wh_question]
        else:
            video_code = url[wh + 7 :]

        return video_code

    def input2code_standard(url):
        parsed_elements = urlparse(url)
        elements = parse_qs(parsed_elements.query)
        if "v" in elements:
            return elements["v"][0]
        else:
            return None

    def get_link_classic(self):
        return "https://www.youtube.com/watch?v={0}".format(self.get_video_code())

    def get_link_mobile(self):
        return "https://www.m.youtube.com/watch?v={0}".format(self.get_video_code())

    def get_link_youtu_be(self):
        return "https://youtu.be/{0}".format(self.get_video_code())

    def get_link_embed(self):
        return "https://www.youtube.com/embed/{0}".format(self.get_video_code())

    def get_link_music(self):
        return "https://music.youtube.com?v={0}".format(self.get_video_code())

    def get_channel_name(self):
        pass

    def get_social_data(self):
        url = self.get_page_url(self.get_return_dislike_url_link())

        response = url.get_response()
        if response.is_valid():
            self.return_dislike_json = ReturnDislikeJson(contents=response.get_text())

        return super().get_social_data()

    def get_return_dislike_url_link(self):
        return "https://returnyoutubedislikeapi.com/votes?videoId=" + self.get_video_code()

    def get_view_count(self):
        """ """
        if self.return_dislike_json:
            return self.return_dislike_json.get_view_count()

    def get_rating(self):
        if self.return_dislike_json:
            return self.return_dislike_json.get_rating()

    def get_thumbs_up(self):
        if self.return_dislike_json:
            return self.return_dislike_json.get_thumbs_up()

    def get_thumbs_down(self):
        if self.return_dislike_json:
            return self.return_dislike_json.get_thumbs_down()
