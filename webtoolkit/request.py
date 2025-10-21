"""
"""

import urllib.parse


REQUEST_TYPE_PING="ping"
REQUEST_TYPE_HEAD="head"
REQUEST_TYPE_FULL="full"


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
        request_type=None,
        ssl_verify=None,
        respect_robots=None,
        settings=None,
        crawler_name=None,
        crawler_type=None,
    ):
        self.url = url
        self.user_agent = user_agent
        self.request_headers = request_headers
        self.timeout_s = timeout_s
        self.request_type=request_type
        self.ssl_verify = respect_robots
        self.respect_robots = respect_robots
        self.settings=settings
        self.crawler_name = crawler_name
        self.crawler_type = crawler_type

    def __str__(self):
        return "Url:{} Timeout:{} Type:{}".format(self.url, self.timeout_s, self.request_type)


def request_to_json(request):
    """TODO"""
    json = {}

    json["url"] = request.url

    if request.user_agent:
        json["User-Agent"] = request.user_agent
    if request.request_headers:
        json["request_headers"] = request.request_headers
    if request.timeout_s is not None:
        json["timeout_s"] = request.timeout_s
    if request.request_type:
        json["request_type"] = request.request_type
    if request.ssl_verify is not None:
        json["ssl_verify"] = request.ssl_verify
    if request.respect_robots is not None:
        json["respect_robots"] = request.respect_robots
    if request.settings:
        json["settings"] = request.settings
    if request.crawler_name:
        json["crawler_name"] = request.crawler_name
    if request.crawler_type:
        json["crawler_type"] = request.crawler_type

    return json


def encode_field(data):
    if data:
        return urllib.parse.quote(data, safe="")


def json_to_request(json_data):
    if "url" not in json_data:
        return

    request = PageRequestObject(json_data["url"])
    request.url = json_data.get("url")
    request.user_agent = json_data.get("User-Agent")
    request.request_headers = json_data.get("request_headers")
    request.timeout_s = json_data.get("timeout_s")
    request.request_type = json_data.get("request_type")
    request.ssl_verify = json_data.get("ssl_verify")
    request.respect_robots = json_data.get("respect_robots")
    request.settings = json_data.get("settings")
    request.crawler_name = json_data.get("crawler_name")
    request.crawler_type = json_data.get("crawler_type")

    return request


def request_encode(request):
    """TODO"""
    json_data = request_to_json(request)
    return urllib.parse.urlencode(json_data)


def request_quote(request):
    """TODO"""
    json_data = request_to_json(request)

    return urllib.parse.quote(json_data, safe="")
