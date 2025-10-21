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
        request_type=False,
        ssl_verify=True,
        respect_robots=True,
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
    json["User-Agent"] = request.user_agent
    return json


def json_to_request(json_data):
    if "url" not in json_data:
        return

    request = PageRequestObject(json_data["url"])
    request.url = json_data.get("url")
    request.user_agent = json_data.get("User-Agent")
    return request


def request_encode(request):
    """TODO"""
    json_data = request_to_json(request)

    return urllib.parse.quote(crawler_data, safe="")
