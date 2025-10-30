"""
"""

import urllib.parse


REQUEST_TYPE_PING = "ping"
REQUEST_TYPE_HEAD = "head"
REQUEST_TYPE_FULL = "full"


class PageRequestObject(object):
    """
    Precise information for scraping.
    Should contain information about what is to be scraped. Means of scraping should not be apart of this.

    @example Url, timeout is OK.
    @example Scarping script name, port, is not OK
    """

    def __init__(
        self,
        url,
        user_agent=None,
        request_headers=None,
        timeout_s=None,
        delay_s=None,
        request_type=None,
        ssl_verify=None,
        respect_robots=None,
        accept_types=None,
        bytes_limit=None,
        settings=None,
        cookies=None,
        crawler_name=None,
        crawler_type=None,
        handler_name=None,
        handler_type=None,
    ):
        self.url = url
        self.user_agent = user_agent
        self.request_headers = request_headers
        self.timeout_s = timeout_s
        self.delay_s = delay_s
        self.request_type = request_type
        self.ssl_verify = respect_robots
        self.respect_robots = respect_robots
        self.accept_types = accept_types
        self.bytes_limit = bytes_limit
        self.settings = settings
        self.cookies = cookies
        self.crawler_name = crawler_name
        self.crawler_type = crawler_type
        self.handler_name = handler_name
        self.handler_type = handler_type

        if not self.settings:
            self.settings = {}
        if not self.cookies:
            self.cookies = {}

    def __str__(self):
        string = ""
        if self.url:
            string += f"Url: {self.url}"

        if self.timeout_s:
            string += f", timeout_s: {self.timeout_s}"

        if self.request_type:
            string += f", request_type: {self.request_type}"

        if self.crawler_name:
            string += f", crawler_name: {self.crawler_name}"

        if self.handler_name:
            string += f", handler_name: {self.handler_name}"

        return string


def request_to_json(request):
    """TODO"""
    if not request:
        return

    json = {}

    json["url"] = request.url

    if request.user_agent:
        json["User-Agent"] = request.user_agent
    if request.request_headers:
        json["request_headers"] = request.request_headers
    if request.timeout_s is not None:
        json["timeout_s"] = request.timeout_s
    if request.delay_s is not None:
        json["delay_s"] = request.delay_s
    if request.request_type:
        json["request_type"] = request.request_type
    if request.ssl_verify is not None:
        json["ssl_verify"] = request.ssl_verify
    if request.respect_robots is not None:
        json["respect_robots"] = request.respect_robots
    if request.accept_types is not None:
        json["accept_types"] = request.accept_types
    if request.bytes_limit is not None:
        json["bytes_limit"] = request.bytes_limit
    if len(request.settings) > 0:
        json["settings"] = request.settings
    if len(request.cookies) > 0:
        json["cookies"] = request.cookies
    if request.crawler_name:
        json["crawler_name"] = request.crawler_name
    if request.crawler_type:
        json["crawler_type"] = str(request.crawler_type)
    if request.handler_name:
        json["handler_name"] = request.handler_name
    if request.handler_type:
        json["handler_type"] = str(request.handler_type)

    return json


def encode_field(data):
    if data:
        return urllib.parse.quote(data, safe="")


def json_to_request(json_data):
    if not json_data:
        return
    if "url" not in json_data:
        return

    request = PageRequestObject(json_data["url"])
    request.url = json_data.get("url")
    request.user_agent = json_data.get("User-Agent")
    request.request_headers = json_data.get("request_headers")
    request.timeout_s = json_data.get("timeout_s")
    if request.timeout_s is not None:
        request.timeout_s = int(request.timeout_s)
    request.delay_s = json_data.get("delay_s")
    if request.delay_s is not None:
        request.delay_s = int(request.delay_s)
    request.request_type = json_data.get("request_type")
    request.ssl_verify = json_data.get("ssl_verify")
    request.respect_robots = json_data.get("respect_robots")
    request.accept_types = json_data.get("accept_types")
    request.bytes_limit = json_data.get("bytes_limit")
    if request.bytes_limit is not None:
        request.bytes_limit = int(request.bytes_limit)
    request.settings = json_data.get("settings")
    request.cookies = json_data.get("cookies")
    request.crawler_name = json_data.get("crawler_name")
    request.crawler_type = json_data.get("crawler_type")
    request.handler_name = json_data.get("handler_name")
    request.handler_type = json_data.get("handler_type")

    if not request.settings:
        request.settings = {}
    if not request.cookies:
        request.cookies = {}

    return request


def request_encode(request):
    """TODO"""
    json_data = request_to_json(request)
    return urllib.parse.urlencode(json_data)


def request_quote(request):
    """TODO"""
    json_data = request_to_json(request)

    return urllib.parse.quote(json_data, safe="")
