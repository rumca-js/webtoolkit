import json
import os
import base64
from pathlib import Path

from webtoolkit import (
    PageRequestObject,
)


default_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
)


default_headers = {
    "User-Agent": default_user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml,application/rss;q=0.9,*/*;q=0.8",
    "Accept-Charset": "utf-8,ISO-8859-1;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
}


class WebToolsTimeoutException(Exception):
    """Custom exception to indicate a request timeout."""

    def __init__(self, message="The request has timed out."):
        super().__init__(message)


class CrawlerInterface(object):
    def __init__(self, url=None, request=None, settings=None):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        if not request:
            request = PageRequestObject(url)

        self.request = request
        self.response = None

        self.set_settings(settings)

    def set_settings(self, settings):
        if not settings:
            self.settings = {"settings": {}}
            return

        self.settings = settings

        if "settings" not in self.settings:
            self.settings["settings"] = {}

        self.request.request_headers = self.get_request_headers()

        real_settings = {}
        if settings and "settings" in settings:
            real_settings = settings["settings"]

        self.request.timeout_s = self.get_timeout_s()

    def set_url(self, url):
        self.request.url = url

    def run(self):
        """
         - does its job
         - sets self.response
         - we should be able to call run several times

        if crawler can access web, then should return response (may be invalid)

        @return response, None if feature is not available
        """
        return self.response

    def get_default_user_agent(self):
        return default_user_agent

    def get_default_headers(self):
        return default_headers

    def is_response_valid(self):
        if not self.response:
            return False

        if not self.response.is_valid():
            self.response.add_error(
                f"Response not valid. Status:{self.response.status_code}"
            )
            return False

        content_length = self.response.get_content_length()
        byte_limit = self.get_bytes_limit()

        if content_length is not None and byte_limit is not None:
            if content_length > bytes_limit:
                self.response.add_error("Page is too big: ".format(content_length))
                return False

        content_type = self.response.get_content_type_keys()
        content_type_keys = self.response.get_content_type_keys()
        if content_type_keys:
            if "all" in self.get_accept_types():
                return True

            match_count = 0
            for item in content_type_keys:
                if item in self.get_accept_types():
                    match_count += 1

            if match_count == 0:
                self.response.add_error(
                    "Response type is not supported:{}".format(content_type)
                )
                return False

        return True

    def get_response(self):
        return self.response

    def is_valid(self):
        return False

    def close(self):
        pass

    def get_accept_types(self):
        if "settings" not in self.settings:
            return

        accept_string = self.settings["settings"].get("accept_content_types")
        if not accept_string:
            accept_string = "all"

        semicolon_index = accept_string.find(";")
        if semicolon_index >= 0:
            accept_string = accept_string[:semicolon_index]

        result = set()
        # Split by comma to separate media types
        media_types = accept_string.split(",")
        for media in media_types:
            # Further split each media type by '/' and '+'
            parts = media.strip().replace("+", "/").split("/")
            for part in parts:
                if part:
                    result.add(part.strip())

        return list(result)

    def get_request_headers(self):
        real_settings = self.settings["settings"]
        headers = real_settings.get("request_headers")

        if headers and len(headers) > 0:
            return headers

        return default_headers

    def get_timeout_s(self):
        real_settings = self.settings["settings"]

        timeout_s = real_settings.get("timeout_s")
        if timeout_s is not None:
            return timeout_s

        return 20

    def get_bytes_limit(self):
        real_settings = self.settings["settings"]

        bytes_limit = real_settings.get("bytes_limit")
        return bytes_limit

    def get_response_file(self):
        real_settings = self.settings["settings"]

        response_file = real_settings.get("response_file")
        return response_file
