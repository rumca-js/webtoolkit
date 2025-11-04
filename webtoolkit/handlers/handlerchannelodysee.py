from concurrent.futures import ThreadPoolExecutor

from ..urllocation import UrlLocation
from ..webtools import WebLogger
from .defaulturlhandler import DefaultRssChannelHandler, DefaultRssHtmlChannelHandler
from .handlerhttppage import HttpPageHandler


class OdyseeChannelHandler(DefaultRssHtmlChannelHandler):

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

    def get_channel_code(self):
        return self.code

    def get_channel_url(self):
        return self.code2url(self.code)

    def get_channel_feed(self):
        return self.code2feed(self.code)

    def get_response(self):
        if not self.code:
            return

        if self.response:
            return self.response

        if self.dead:
            return

        if not self.threads:
            self.rss_url = self.get_rss_url()
            self.html_url = self.get_html_url()

            if self.rss_url:
                self.response = self.rss_url.get_response()
            else:
                WebLogger.error("Could not obtain RSS")
            if self.html_url:
                self.response_html = self.html_url.get_response()
            else:
                WebLogger.error("Could not obtain HTML")
        else:
            with ThreadPoolExecutor() as executor:
                thread_result_rss = executor.submit(self.get_rss_url)
                thread_result_html = executor.submit(self.get_html_url)

                rss_url = thread_result_rss.result()
                html_url = thread_result_html.result()

                if rss_url:
                    self.response = rss_url.get_response()
                else:
                    WebLogger.error("Could not obtain RSS")
                if html_url:
                    self.html_response = html_url.get_response()
                else:
                    WebLogger.error("Could not obtain HTML")

        return self.response

    def get_html_url(self):
        #print("get_html_url")
        if self.html_url:
            return self.html_url

        self.html_url = self.get_page_url(self.get_channel_url())
        if not self.html_url:
            return

        self.html_url.get_response()

        #print("get_html_url DONE")
        return self.html_url

    def get_title(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_title()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_title()

    def get_description(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_description()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_description()

    def get_language(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_language()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_language()

    def get_thumbnail(self):
        rss_url = self.get_rss_url()
        if rss_url:
            thumbnail = rss_url.get_thumbnail()
            if thumbnail:
                return thumbnail
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_thumbnail()

    def get_author(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_author()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_author()

    def get_album(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_album()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_album()

    def get_tags(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_tags()
        html_url = self.get_html_url()
        if html_url:
            return html_url.get_tags()

