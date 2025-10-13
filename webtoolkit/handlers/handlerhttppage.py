import subprocess
import json
import os
import time
import traceback
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from datetime import timedelta

from utils.dateutils import DateUtils

from ..pages import (
    HtmlPage,
    RssPage,
    PageFactory,
)
from ..urllocation import UrlLocation

from ..request import PageRequestObject, PageOptions

from ..response import PageResponseObject

from ..webtools import *

from ..statuses import *
from .handlerinterface import HandlerInterface


class HttpPageHandler(HandlerInterface):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url=url, contents=contents, settings=settings, url_builder=url_builder
        )
        self.p = None
        self.response = None
        self.settings = settings

    def is_handled_by(self):
        url = self.url

        if url.startswith("https") or url.startswith("http"):
            return True
        return False

    def get_contents(self):
        """
        Obtains only contents
        """
        if self.response and self.response.get_text():
            return self.response.get_text()

        self.get_response_implementation()

        if self.response and self.response.get_text():
            return self.response.get_text()

    def get_response(self):
        """
        Obtains response, analyzes structure, etc
        """
        if self.response:
            return self.response

        self.get_response_implementation()

        self.p = self.get_page_handler()

        if self.p and type(self.p) == RssPage:
            if self.response:
                self.response.set_recognized_content_type("application/rss+xml")
        elif self.p and type(self.p) == HtmlPage:
            if self.response:
                self.response.set_recognized_content_type("text/html")

        if self.p and self.response:
            self.response.set_body_hash(self.get_contents_body_hash())

        if self.response:
            return self.response

    def get_response_implementation(self):
        url = self.url

        dap = UrlLocation(url)

        if self.is_handled_by():
            if not dap.is_media():
                builder = HttpRequestBuilder(url=url, settings=self.settings)
                self.response = builder.get_response()

                if not self.response:
                    return

    def get_page_handler(self):
        """
        Note: some servers might return text/html for RSS sources.
              We must manually check what kind of data it is.
              For speed - we check first what is suggested by content-type
        """
        if self.p:
            return self.p

        contents = None
        if self.response and self.response.get_text():
            contents = self.response.get_text()

        if not contents:
            return

        url = self.url

        self.p = PageFactory.get(self.response, contents)
        return self.p

    def get_title(self):
        if not self.p:
            return
        return self.p.get_title()

    def get_description(self):
        if not self.p:
            return
        return self.p.get_description()

    def get_language(self):
        if not self.p:
            return
        return self.p.get_language()

    def get_thumbnail(self):
        if not self.p:
            return
        return self.p.get_thumbnail()

    def get_author(self):
        if not self.p:
            return
        return self.p.get_author()

    def get_album(self):
        if not self.p:
            return
        return self.p.get_album()

    def get_tags(self):
        if not self.p:
            return
        return self.p.get_tags()

    def get_date_published(self):
        if not self.p:
            return
        return self.p.get_date_published()

    def get_canonical_url(self):
        if not self.get_response():
            self.get_response()

        if not self.p:
            return self.url
        return self.p.get_canonical_url()

    def get_properties(self):
        if not self.p:
            return

        props = self.p.get_properties()
        props["status_code"] = self.response.status_code
        return props

    def get_page_rating_vector(self):
        result = []
        if not self.p:
            return result

        """
        TODO include this somehow
        """
        if self.response:
            result.append(self.get_page_rating_status_code(self.response.status_code))

        result.extend(self.p.get_page_rating_vector())
        return result

    def get_contents_hash(self):
        if not self.p:
            return super().get_contents_hash()

        return self.p.get_contents_hash()

    def get_contents_body_hash(self):
        if not self.p:
            return super().get_contents_body_hash()

        return self.p.get_contents_body_hash()

    def get_page_rating_status_code(self, status_code):
        rating = 0
        if status_code == 200:
            rating += 10
        elif status_code > 200 and status_code < 300:
            rating += 5
        elif status_code >= 300 and status_code < 400:
            rating += 1
        elif status_code != 0:
            rating += 0

        return [rating, 10]

    def get_status_code(self):
        if not self.response:
            return PageResponseObject.STATUS_CODE_UNDEF

        return self.response.status_code

    def is_valid(self):

        # not valid HTTP response
        response = self.response
        if not response or not response.is_valid():
            return False

        if self.p:
            return self.p.is_valid()

        return True

    def get_favicon(self):
        if self.p:
            if type(self.p) is HtmlPage:
                favs = self.p.get_favicons()
                if favs and len(favs) > 0:
                    return list(favs.keys())[0]

    def get_entries(self):
        if self.p:
            if type(self.p) is RssPage:
                return self.p.get_entries()
            if type(self.p) is HtmlPage:
                # There might be RSS in HTML
                rss = RssPage(self.url, self.p.get_contents())
                if rss.is_valid():
                    return rss.get_entries()
        return []

    def get_feeds(self):
        result = []
        url = self.url

        feeds = super().get_feeds()
        if feeds and len(feeds) > 0:
            result.extend(feeds)

        if not self.p:
            return result

        feeds = self.p.get_feeds()
        if feeds and len(feeds) > 0:
            result.extend(feeds)

        return result


class HttpRequestBuilder(object):
    """
    Makes actual request using crawler.
    This should be just a builder.
    Should not contain any HTML/RSS content processing.
    """

    def __init__(self, url=None, settings=None):
        """
        @param url URL
        @param contents URL page contents
        @param use_selenium decides if selenium is used
        """
        self.response = None
        self.url = url
        self.settings = settings
        self.errors = []

        # Flag to not retry same contents requests for things we already know are dead
        self.dead = False

        if self.url is None:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            self.errors.append("Passed incorrect url {}".format(stack_str))
            return

        # TODO remove things below?
        if self.url.lower().find("https") >= 0:
            self.protocol = "https"
        elif self.url.lower().find("http") >= 0:
            self.protocol = "http"
        else:
            self.protocol = "https"

    def get_response(self):
        if self.response:
            return self.response

        if self.dead:
            return None

        self.get_response_implementation()

        return self.response

    def get_text(self):
        response = self.get_response()
        if response:
            return response.get_text()

    def get_binary(self):
        response = self.get_response()
        if response:
            return response.get_binary()

    def get_contents_internal(self):
        """ """
        crawler_data = self.settings

        if not crawler_data:
            return

        if "crawler" not in crawler_data:
            self.errors.append("Url:{} No crawler in crawler data".format(self.url))
            return

        crawler = crawler_data["crawler"]

        crawler.set_url(self.url)
        crawler.set_settings(crawler_data)

        start_time = time.time()
        crawler.run()
        end_time = time.time()

        response = crawler.get_response()
        if response:
            response.set_crawler(crawler_data)
            if response.errors:
                for error in response.errors:
                    self.errors.append(error)

            response.crawl_time_s = end_time - start_time
        crawler.close()

        if response:
            return response

        self.dead = True
        self.errors.append("Url:{} No response from crawler".format(self.url))

        self.response = PageResponseObject(
            self.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.url,
        )
        return self.response

    def get_response_implementation(self):
        if self.response and self.response.text:
            return self.response

        if self.dead:
            return None

        if not self.is_url_valid():
            lines = traceback.format_stack()
            line_text = ""
            for line in lines:
                line_text += line

            self.errors.append("Url:{} is invalid. Lines:{}".format(self.url, line_text))

            self.dead = True
            return None

        self.response = self.get_contents_internal()

        return self.response

    def is_url_valid(self):
        if self.url == None:
            return False

        p = UrlLocation(self.url)
        if not p.is_web_link():
            return False

        return True
