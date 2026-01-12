"""
Default url handler.
"""

import copy
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from ..utils.dateutils import DateUtils
from ..pages import DefaultContentPage
from ..request import PageRequestObject, copy_request
from ..webconfig import WebLogger
from ..webtools import calculate_hash
from .handlerhttppage import HttpPageHandler


class DefaultUrlHandler(HttpPageHandler):
    """
    Default URL handler
    """

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
            WebLogger.error("Default Url Handler - no url")
            return

        if self.url == url and self.request is not None:
            request = copy.copy(self.request)
        else:
            if self.url_builder:
                # some handlers might provide custom crawlers for urls
                request = self.url_builder(url).get_request_for_url(url)
            else:
                request = PageRequestObject(url)
            request.url = url
            # request.handler_type = HttpPageHandler # object will be assigned by builder

        # if we will not hardcode this handler, then it will recursively loop
        request.handler_name = "HttpPageHandler"
        request.handler_type = None  # object will be assigned by builder

        if crawler_name:
            request.crawler_name = crawler_name
            request.crawler_type = None

        if self.url_builder:
            url = self.url_builder(
                url=url, request=request, url_builder=self.url_builder
            )
            return url

        WebLogger.error("Default Url Handler - no builder")

    def build_default_url(self, url, crawler_name=None):
        """
        TODO reneme get_page_url to build_http_url
        """
        if not url:
            return

        if self.url_builder:
            # some handlers might provide custom crawlers for urls
            request = self.url_builder(url).get_request_for_url(url)
        else:
            request = PageRequestObject(url)

        request.url = url
        if self.request:
            request.timeout_s = self.request.timeout_s

        request.crawler_type = None
        if crawler_name:
            request.crawler_name = crawler_name

        if self.url_builder:
            url = self.url_builder(
                url=url, request=request, url_builder=self.url_builder
            )
            return url

    def get_code(self):
        return self.code


class DefaultChannelHandler(DefaultUrlHandler):
    """
    Default handler for channels
    """

    def get_channel_name(self):
        return self.get_title()

    def get_channel_url(self):
        if self.code:
            return self.code2url(self.code)


class DefaultCompoundChannelHandler(DefaultChannelHandler):
    """
    Default URL handler which is capable of obtaining data from many network sources automatically.
    """

    def __init__(self, url=None, contents=None, request=None, url_builder=None):
        self.responses = []
        self.channel_sources_urls = OrderedDict()
        super().__init__(url=url, request=request, url_builder=url_builder)

    def get_channel_sources(self):
        sources = []

        feeds = self.get_feeds()
        if feeds and len(feeds) > 0:
            feed = feeds[0]
            if feed:
                sources.append(feed)

        channel_url = self.get_channel_url()
        if channel_url:
            sources.append(channel_url)

        if len(sources) == 0:
            sources.append(self.url)

        return sources

    def get_contents(self):
        """
        We obtain information about channel.
        We cannot use HTML page to obtain thumbnail - as web page asks to log in to view this
        """
        if self.contents:
            return self.contents

        if self.get_response():
            return self.get_response().get_text()

    def get_response(self):
        responses = self.get_responses()
        if responses and len(responses) > 0:
            return responses[0]

    def get_responses(self):
        if self.responses and len(self.responses) > 0:
            return self.responses

        return self.get_responses_implementation(self.get_channel_sources())

    def get_responses_implementation(self, channel_sources):
        handles = []
        with ThreadPoolExecutor() as executor:
            for channel_source in channel_sources:
                if channel_source not in self.channel_sources_urls:
                    handles.append(
                        executor.submit(self.get_response_source, channel_source)
                    )

            for handle in handles:
                url = handle.result()

                url.get_response()

                self.channel_sources_urls[url.url] = url

        # we capture responses using order of urls
        for page_url in self.channel_sources_urls.values():
            self.responses.append(page_url.get_response())

        return self.responses

    def is_valid(self):
        is_valid = True
        for page_url in self.channel_sources_urls.values():
            response = url.get_response()
            if not response.is_valid():
                is_valid = False
        return is_valid

    def is_invalid(self):
        is_invalid = True
        for page_url in self.channel_sources_urls.values():
            response = url.get_response()
            if not response.is_invalid():
                is_invalid = False
        return is_invalid

    def get_hash(self):
        text = ""
        for page_url in self.channel_sources_urls.values():
            response = page_url.get_response()
            text += str(response.get_text())
        return calculate_hash(text)

    def get_feeds(self):
        feeds = set()

        for page_url in self.channel_sources_urls.values():
            feeds.update(page_url.get_feeds())

        return list(feeds)

    def get_streams(self):
        for page_url in self.channel_sources_urls.values():
            self.streams[page_url.url] = page_url.get_response()

        return self.streams

    def get_response_source(self, page_url):
        if page_url in self.channel_sources_urls.values():
            return self.channel_sources_urls[page_url]

        url = self.get_page_url(page_url)
        if url:
            url.get_response()

        return url

    def get_entries(self):
        for url in self.channel_sources_urls.values():
            entries = url.get_entries()
            if entries and len(list(entries)) > 0:
                return entries
        return []

    def get_title(self):
        for url in self.channel_sources_urls.values():
            title = url.get_title()
            if title:
                return title

    def get_description(self):
        for url in self.channel_sources_urls.values():
            description = url.get_description()
            if description:
                return description

    def get_language(self):
        for url in self.channel_sources_urls.values():
            language = url.get_language()
            if language:
                return language

    def get_thumbnail(self):
        for url in self.channel_sources_urls.values():
            thumbnail = url.get_thumbnail()
            if thumbnail:
                return thumbnail

    def get_author(self):
        for url in self.channel_sources_urls.values():
            author = url.get_author()
            if author:
                return author

    def get_album(self):
        for url in self.channel_sources_urls.values():
            album = url.get_author()
            if album:
                return album

    def get_tags(self):
        for url in self.channel_sources_urls.values():
            tags = url.get_tags()
            if tags:
                return tags

    def get_date_published(self):
        for url in self.channel_sources_urls.values():
            date_published = url.get_date_published()
            if date_published:
                return date_published
