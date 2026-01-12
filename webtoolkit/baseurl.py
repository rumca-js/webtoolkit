"""
Url handling class.

@example
url = BaseUrl(link = "https://google.com")
response = url.get_response()
"""

import base64
from typing import Any, Callable, Optional, Type

from .utils.dateutils import DateUtils

from .pages import (
    ContentInterface,
    DefaultContentPage,
    RssPage,
    HtmlPage,
)
from .webtools import (
    calculate_hash,
    WebLogger,
)
from .urllocation import (
    UrlLocation,
    URL_TYPE_RSS,
    URL_TYPE_CSS,
    URL_TYPE_JAVASCRIPT,
    URL_TYPE_HTML,
    URL_TYPE_FONT,
    URL_TYPE_UNKNOWN,
)

from .statuses import status_code_to_text
from .response import response_to_json
from .request import request_to_json, PageRequestObject
from .handlers import (
    HandlerInterface,
    HttpPageHandler,
    OdyseeVideoHandler,
    OdyseeChannelHandler,
    RedditUrlHandler,
    ReturnDislike,
    GitHubUrlHandler,
    HackerNewsHandler,
    InternetArchive,
    FourChanChannelHandler,
    TwitterUrlHandler,
    YouTubeVideoHandler,
    YouTubeChannelHandler,
)

from .crawlers import (
    RequestsCrawler,
)
from .domaincache import DomainCache


class BaseUrl(ContentInterface):
    """
    Base Url class capable of reading network pages.
    """

    def __init__(self, url=None, request=None, url_builder=None):
        """
        Constructor
        """
        if not request and url:
            self.request_url = url
            self.request = self.get_request_for_url(url)
        else:
            self.request_url = request.url
            self.request = request

        if not self.request.crawler_type:
            self.request = self.get_request_for_request(self.request)

        self.url = self.request.url
        self.handler = None
        self.response = None
        self.url_builder = url_builder

        if self.request.url:
            self.request.url = self.get_cleaned_link()
        else:
            WebLogger.error("Url needs to be specified")
            return

        if not self.url_builder:
            self.url_builder = BaseUrl

    def get_request_for_url(self, url):
        request = PageRequestObject(url)
        request.crawler_name = "RequestsCrawler"
        request.crawler_type = RequestsCrawler(url)

        return request

    def get_request_for_request(self, request):
        request.crawler_name = "RequestsCrawler"
        request.crawler_type = RequestsCrawler(request.url)

        return request

    def get_handlers(self):
        """
        Returns available handlers.
        Order is important - from the most precise handler to the most general.
        """
        # fmt off

        return [
            YouTubeVideoHandler,
            OdyseeVideoHandler,
            OdyseeChannelHandler,
            RedditUrlHandler,
            ReturnDislike,
            GitHubUrlHandler,
            HackerNewsHandler,
            InternetArchive,
            FourChanChannelHandler,
            TwitterUrlHandler,
            YouTubeChannelHandler,  # present here, if somebody wants to call it by name
            HttpPageHandler,  # default
        ]
        # fmt on

    def get_handler_by_name(self, handler_name):
        """Returns handler class"""
        handlers = self.get_handlers()
        for handler in handlers:
            if handler.__name__ == handler_name:
                return handler

    def get_handler(self):
        """
        Returns handler object.
        @note This function does not fetch response.
        """
        if self.handler:
            return self.handler

        self.handler = self.get_handler_implementation()
        return self.handler

    def get_type(self):
        """
        Based on link structure identify type.
        Should provide a faster means of obtaining handler, without the need
        to obtain the page

        TODO maybe we should 'ping page' to see status
        """
        # based on link 'appearance'

        url = self.request.url

        if not url:
            return

        p = UrlLocation(url)
        short_url = p.get_protocolless()
        if not short_url:
            return

        handlers = self.get_handlers()
        for handler in handlers:
            if handler(url=url).is_handled_by():
                if handler == HttpPageHandler:
                    page_type = UrlLocation(url).get_type()

                    # TODO this should return HttpPageHandler?

                    if page_type == URL_TYPE_HTML:
                        return HtmlPage(url, "")

                    if page_type == URL_TYPE_RSS:
                        return RssPage(url, "")

                    if url.find("rss") >= 0:
                        return RssPage(url, "")
                    if url.find("feed") >= 0:
                        return RssPage(url, "")

                    return

                return handler(url)

    def get_contents(self):
        """
        Returns text
        """
        if self.get_response():
            return self.get_response().get_text()

    def get_binary(self):
        """
        Returns binary
        """
        response = self.get_response()
        if response:
            return self.response.get_binary()

    def get_response(self):
        """
        Returns full response, with page handling object
        """
        if self.response:
            return self.response

        if not self.handler:
            self.handler = self.get_handler_implementation()

        if self.handler:
            if self.request.respect_robots:
                if not self.is_allowed():
                    return

            self.response = self.handler.get_response()
            if self.response:
                if not self.response.is_valid():
                    WebLogger.error(
                        "Url:{} Response is invalid:{}".format(
                            self.request.url, self.response
                        ),
                        detail_text=str(response_to_json(self.response)),
                    )

            return self.response

    def get_streams(self):
        """
        Returns all responses
        """
        streams = {}
        result = {}

        handler = self.get_handler()

        if handler:
            if self.request.respect_robots:
                if not self.is_allowed():
                    return []

            streams = self.handler.get_streams()

        if streams:
            for key, response in streams.items():
                response_json = response_to_json(response)
                result[key] = response_json

        return result

    def get_headers(self):
        # TODO implement
        pass

    def ping(self, timeout_s=20, user_agent=None):
        # TODO if that fails we would have to find suitable agent, and then ping
        return RequestsCrawler(self.request.url).ping()

    def get_handler_implementation(self):
        """Returns handler"""
        url = self.request.url
        if not url:
            return

        p = UrlLocation(url)
        short_url = p.get_protocolless()

        if not short_url:
            return

        handlers = self.get_handlers()
        for handler in handlers:
            if (
                self.request.handler_name
                and self.request.handler_name != ""
                and self.request.handler_name != handler.__name__
            ):
                continue
            if self.request.handler_type and self.request.handler_type != handler:
                continue

            h = handler(
                url=self.request.url, request=self.request, url_builder=self.url_builder
            )
            if h.is_handled_by():
                self.request.url = h.url
                return h

        if url.startswith("https") or url.startswith("http"):
            return HttpPageHandler(
                url=url, request=self.request, url_builder=self.url_builder
            )
        elif url.startswith("smb") or url.startswith("ftp"):
            raise NotImplementedError("Protocol has not been implemented")

    def get_cleaned_link(self):
        """Returns cleaned up link. Free of unwanted args, tracking, sanitized."""
        url = self.request.url

        url = url.strip()

        if url.endswith("/"):
            url = url[:-1]
        if url.endswith("."):
            url = url[:-1]

        # domain is lowercase
        return UrlLocation.get_cleaned_link(url)

    def get_url(self):
        self.get_handler()
        if self.handler:
            return self.handler.get_url()
        else:
            return self.request.url

    def get_urls(self):
        """Returns various link versions for URL"""
        properties = {}
        properties["link"] = self.request.url
        properties["link_request"] = self.request_url
        canonical = self.get_canonical_url()
        if canonical:
            properties["link_canonical"] = canonical
        return properties

    def get_canonical_url(self):
        """Returns canonical link"""
        if self.handler:
            return self.handler.get_canonical_url()

        handlers = self.get_handlers()
        for handler_class in handlers:
            handler = handler_class(url=self.request.url)
            if handler.is_handled_by():
                return handler.get_canonical_url()

    def get_urls_archive(self):
        """Returns archive link for URL"""
        p = UrlLocation(self.request.url)
        short_url = p.get_protocolless()

        properties = []

        archive = InternetArchive(self.request.url)
        properties.append(archive.get_archive_url())

        properties.append("https://archive.ph/" + short_url)

        return properties

    def __str__(self):
        return "{}".format(self.request)

    def is_valid(self):
        """Returns indication if URL is valid"""
        if not self.handler:
            return False

        if self.response is None:
            return False

        if self.response and not self.response.is_valid():
            return False

        if not self.handler.is_valid():
            return False

        return True

    def get_title(self):
        """Returns title"""
        if self.handler:
            return self.handler.get_title()

    def get_description(self):
        """Returns description"""
        if self.handler:
            return self.handler.get_description()

    def get_language(self):
        """Returns language"""
        if self.handler:
            return self.handler.get_language()

    def get_thumbnail(self):
        """Returns thumbnail"""
        if self.handler:
            return self.handler.get_thumbnail()

    def get_author(self):
        """Returns author"""
        if self.handler:
            return self.handler.get_author()

    def get_album(self):
        """Returns album"""
        if self.handler:
            return self.handler.get_album()

    def get_tags(self):
        """Returns tags"""
        if self.handler:
            return self.handler.get_tags()

    def get_date_published(self):
        """Returns date published"""
        if self.handler:
            return self.handler.get_date_published()

    def get_status_code(self) -> int | None:
        """Returns status code"""
        if self.response:
            return self.response.get_status_code()

        return 0

    def get_entries(self):
        """Returns entries list"""

        handler = self.get_handler()
        if handler:
            return handler.get_entries()
        else:
            return []

    def find_rss_url(self):
        """
        TODO remove
        """
        url = self.url

        if not url:
            return

        handler = self.get_handler()

        if handler:
            if type(handler) is HttpPageHandler:
                if type(handler.p) is RssPage:
                    return self

        # maybe our handler is able to produce feed without asking for response

        feeds = self.get_feeds()
        if url in feeds:
            return self

        if feeds and len(feeds) > 0:
            u = self.url_builder(url=feeds[0])
            return u

    def get_feeds(self):
        """Returns feeds found for URL"""
        result = []

        handler = self.get_handler()
        if handler:
            return list(set(handler.get_feeds()))

        return result

    def calculate_hash(self, text):
        return calculate_hash(text)

    def get_hash(self):
        """Returns hash for URL"""
        handler = self.get_handler()
        if handler:
            return handler.get_hash()

    def get_body_hash(self):
        """Returns body hash for URL"""
        handler = self.get_handler()
        if handler:
            return handler.get_body_hash()

    def get_meta_hash(self) -> Optional[str]:
        """
        Calculates and returns a hash of the page's metadata properties.
        :return: A base64-encoded hash of the properties.
        """
        self.get_response()
        properties_data = self.get_properties_data()
        properties_hash = self.property_encode(calculate_hash(str(properties_data)))
        return properties_hash

    def get_properties(self):
        """
        Returns basic URL properties
        """
        return self.get_properties_data()

    def get_all_properties(self, include_social=False):
        """Returns all URL properties"""
        response = self.get_response()

        properties_data = self.get_properties()

        all_properties = []

        all_properties.append({"name": "Properties", "data": properties_data})

        properties_hash = self.property_encode(calculate_hash(str(properties_data)))
        all_properties.append({"name": "PropertiesHash", "data": properties_hash})

        if response:
            if response.get_text():
                all_properties.append(
                    {"name": "Text", "data": {"Contents": response.get_text()}}
                )
            elif response.get_binary():
                all_properties.append(
                    {
                        "name": "Binary",
                        "data": {
                            "Contents": self.property_encode(response.get_binary())
                        },
                    }
                )

        streams = self.get_streams()
        all_properties.append({"name": "Streams", "data": streams})

        # TODO request is part of response now. Should we include it?
        request_data = request_to_json(self.request)
        request_data["crawler_type"] = type(request_data["crawler_type"]).__name__
        all_properties.append({"name": "Request", "data": request_data})

        response_data = self.get_response_data()
        all_properties.append({"name": "Response", "data": response_data})
        if response:
            raw_headers_data = response.get_headers()
            all_properties.append({"name": "Headers", "data": raw_headers_data})
        else:
            all_properties.append({"name": "Headers", "data": None})

        if include_social:
            social_data = self.get_social_properties(self.request.url)
            if social_data:
                all_properties.append({"name": "Social", "data": social_data})

        entries_data = self.get_entry_data()
        all_properties.append({"name": "Entries", "data": entries_data})

        return all_properties

    def get_properties_data(self):
        """Returns simple meta properties.
        TODO there should two functions: get_all_properties and get_properties"""
        properties = super().get_properties()
        page_handler = self.get_handler()

        properties["link_request"] = self.request_url

        feeds = self.get_feeds()
        if len(feeds) > 0:
            properties["feeds"] = []
            for key, feed in enumerate(feeds):
                properties["feeds"].append(feed)

        is_channel = False
        channel_handler = YouTubeChannelHandler(url=self.url)
        if channel_handler.is_handled_by():
            is_channel = True

        if page_handler:
            """
            TODO detect type of handler. IsChannel?
            """
            if is_channel:
                if page_handler.get_channel_name():
                    properties["channel_name"] = page_handler.get_channel_name()
                    properties["channel_url"] = page_handler.get_channel_url()

            if (
                type(page_handler) is HttpPageHandler
                and type(page_handler.p) is HtmlPage
            ):
                properties["favicon"] = page_handler.p.get_favicon()
                properties["meta title"] = page_handler.p.get_meta_field("title")
                properties["meta description"] = page_handler.p.get_meta_field(
                    "description"
                )
                properties["meta keywords"] = page_handler.p.get_meta_field("keywords")

                properties["og:title"] = page_handler.p.get_og_field("title")
                properties["og:description"] = page_handler.p.get_og_field(
                    "description"
                )
                properties["og:image"] = page_handler.p.get_og_field("image")
                properties["og:site_name"] = page_handler.p.get_og_field("site_name")
                properties["schema:thumbnailUrl"] = page_handler.p.get_schema_field(
                    "thumbnailUrl"
                )

        properties["link_archives"] = self.get_urls_archive()

        return properties

    def response_to_data(self, response):
        """
        Returns response JSON.

        If respect robots is not enabled, then we do not check robots.txt file.
        If we would check it, it would require additional call to fetch robots.
        """
        response_data = response_to_json(response)

        if self.request.respect_robots:
            response_data["is_allowed"] = self.is_allowed()

        return response_data

    def get_response_data(self):
        """
        Returns response data
        Easy digestible response data
        """
        response = self.get_response()
        response_data = self.response_to_data(response)
        return response_data

    def get_entry_data(self):
        index = 0
        result = []

        entries = self.get_entries()

        if entries:
            for entry in entries:
                if "feed_entry" in entry:
                    del entry["feed_entry"]
                result.append(entry)

        return result

    def property_encode(self, byte_property):
        return base64.b64encode(byte_property).decode("utf-8")

    def is_allowed(self) -> bool:
        """
        Returns indication is access is allowed for bots, robots
        """
        domain_info = DomainCache.get_object(
            url=self.request.url, url_builder=self.url_builder
        )
        return domain_info.is_allowed(self.request.url)

    def get_social_properties(self):
        """Returns social properties"""
        url = self.request.url

        json_obj = {}

        handler = self.get_handler()
        if not handler:
            i = HandlerInterface()
            return i.get_social_data()

        json_data = handler.get_json_data()
        return handler.get_social_data()
