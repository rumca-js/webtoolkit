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


class CrawlerInterface(object):
    def __init__(self, request=None, url=None, response_file=None, settings=None):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        if not request:
            request = PageRequestObject(url)

        self.request = request
        self.response = None
        self.response_file = response_file
        self.request_headers = None

        if settings:
            if "settings" not in settings:
                settings["settings"] = {}
            self.set_settings(settings)
        else:
            self.settings = {"settings": {}}

    def set_settings(self, settings):
        self.settings = settings

        if (
            self.settings
            and "headers" in self.settings
            and self.settings["headers"]
            and len(self.settings["headers"]) > 0
        ):
            self.request_headers = self.settings["headers"]
        elif (
            self.request
            and self.request.request_headers
            and len(self.request.request_headers) > 0
        ):
            self.request_headers = self.request.request_headers
        else:
            self.request_headers = default_headers

        real_settings = {}
        if settings and "settings" in settings:
            real_settings = settings["settings"]

        if self.request.timeout_s and "timeout_s" in real_settings:
            self.timeout_s = max(self.request.timeout_s, real_settings["timeout_s"])
        elif self.request.timeout_s:
            self.timeout_s = self.request.timeout_s
        elif "timeout_s" in real_settings:
            self.timeout_s = real_settings["timeout_s"]
        else:
            self.timeout_s = 10

    def set_url(self, url):
        self.request.url = url

    def get_accept_types(self):
        if "settings" not in self.settings:
            return

        accept_string = self.settings["settings"].get("accept_content_types", "all")

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

    def run(self):
        """
         - does its job
         - sets self.response
         - clears everything from memory, it created

        if crawler can access web, then should return response (may be invalid)

        @return response, None if feature is not available
        """
        return self.response

    def is_response_valid(self):
        if not self.response:
            return False

        if not self.response.is_valid():
            self.response.add_error(
                f"Response not valid. Status:{self.response.status_code}"
            )
            return False

        content_length = self.response.get_content_length()

        if content_length is not None and "bytes_limit" in self.settings["settings"]:
            if content_length > self.settings["settings"]["bytes_limit"]:
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
