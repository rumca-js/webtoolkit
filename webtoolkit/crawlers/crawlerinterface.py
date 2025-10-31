import json
import os
import base64
from pathlib import Path
import ua_generator

from webtoolkit import (
    PageRequestObject,
)


def get_default_headers(device=None, browser=None):
    if not device:
        device = "desktop"
    if not browser:
        browser = ["chrome", "edge"]

    ua = ua_generator.generate(device=device, browser=browser)
    headers = ua.headers.get()

    if "user-agent" in headers:
        headers["User-Agent"] = headers["user-agent"]
        del headers["user-agent"]

    return headers


def get_default_user_agent(device=None, browser=None):
    headers = get_default_headers(device, browser)
    if "User-Agent" in headers:
        return headers["User-Agent"]


class WebToolsTimeoutException(Exception):
    """Custom exception to indicate a request timeout."""

    def __init__(self, message="The request has timed out."):
        super().__init__(message)


class CrawlerInterface(object):
    """
    Crawler is a tool that allows to obtain contents from the internet.
    There are various tools.
    """
    def __init__(self, url=None, request=None):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        if not request:
            request = PageRequestObject(url)

        self.request = request
        self.response = None

    def update_request(self):
        # self.request.request_headers = self.get_request_headers()
        # self.request.timeout_s = self.get_timeout_s()
        # TODO
        # Fill fields not set by default
        pass

    def set_url(self, url):
        self.request.url = url

    def make_request(self, request):
        self.request = request

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
        return get_default_user_agent()

    def get_default_headers(self):
        return get_default_headers()

    def is_response_valid(self):
        if not self.response:
            return False

        if not self.response.is_valid():
            self.response.add_error(
                f"Response not valid. Status:{self.response.status_code}"
            )
            return False

        content_length = self.response.get_content_length()
        bytes_limit = self.get_bytes_limit()

        if content_length is not None and bytes_limit is not None:
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
        accept_string = self.request.accept_types
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
        headers = self.request.request_headers
        custom_user_agent = self.request.user_agent

        if not headers or len(headers) == 0:
            headers = self.get_default_headers()

        if custom_user_agent:
            headers["User-Agent"] = custom_user_agent

        if "User-Agent" not in headers:
            headers["User-Agent"] = self.get_default_user_agent()

        return headers

    def get_user_agent(self):
        headers = self.request.request_headers
        custom_user_agent = self.request.user_agent

        if custom_user_agent:
            return custom_user_agent

        return self.get_default_user_agent()

    def get_timeout_s(self):
        timeout_s = self.request.timeout_s

        if timeout_s is not None:
            return timeout_s

        return 20

    def get_bytes_limit(self):
        bytes_limit = self.request.bytes_limit
        return bytes_limit

    def get_response_file(self):
        if self.request.settings:
            real_settings = self.request.settings

            response_file = real_settings.get("response_file")
            return response_file
