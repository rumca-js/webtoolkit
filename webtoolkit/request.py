"""
"""

import html
import json

from .webtools import date_str_to_date
from .ipc import string_to_command



class PageOptions(object):
    """
    Page request options. Serves more like request API.

    API user defines if headless browser is required.
    WebTools can be configured to use a script, port, or whatever

    Fields:
     - ping - only check status code, and headers of page. Does not download contents
     - browser promotions - if requests cannot receive response we can try with headless or full browser
     - user_agent - not supported by all crawlers. Selenium, stealth requests uses their own agents
     - mode_mapping - configuration of modes
    """

    def __init__(self):
        self.ssl_verify = True
        self.ping = False
        self.use_browser_promotions = (
            True  # tries next mode if normal processing does not work
        )

        self.mode_mapping = {}

        self.user_agent = None  # passed if you wish certain user agent to be used

    def is_mode_mapping(self):
        if self.mode_mapping and len(self.mode_mapping) > 0:
            return True

    def copy_config(self, other_config):
        # if we have mode mapping - use it
        self.mode_mapping = other_config.mode_mapping
        self.ssl_verify = other_config.ssl_verify

    def __str__(self):
        if self.mode_mapping and len(self.mode_mapping) > 0:
            return "Browser:{} P:{} SSL:{} PR:{}".format(
                self.mode_mapping[0],
                self.ping,
                self.ssl_verify,
                self.use_browser_promotions,
            )
        else:
            return "Browser:None P:{} SSL:{} PR:{}".format(
                self.ping,
                self.ssl_verify,
                self.use_browser_promotions,
            )

    def get_str(self):
        return str(self)

    def get_crawler(self, name):
        for mode_data in self.mode_mapping:
            if "enabled" in mode_data:
                if mode_data["name"] == name and mode_data["enabled"] == True:
                    return mode_data
            else:
                if mode_data["name"] == name:
                    return mode_data

    def bring_to_front(self, input_data):
        result = [input_data]
        for mode_data in self.mode_mapping:
            if mode_data == input_data:
                continue

            result.append(mode_data)

        self.mode_mapping = result

    def get_timeout(self, timeout_s):
        if not self.mode_mapping or len(self.mode_mapping) == 0:
            return timeout_s

        first_mode = self.mode_mapping[0]

        if "settings" not in first_mode:
            return timeout_s

        settings = first_mode["settings"]

        if "timeout_s" in settings:
            timeout_crawler = settings["timeout_s"]
            return timeout_crawler

        return timeout_s


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
        headers=None,
        user_agent=None,
        request_headers=None,
        timeout_s=10,
        ping=False,
        ssl_verify=True,
    ):
        self.url = url

        self.user_agent = user_agent

        self.timeout_s = timeout_s
        self.ping = ping
        self.headers = headers
        self.request_headers = request_headers

        self.ssl_verify = True

    def __str__(self):
        return "Url:{} Timeout:{} Ping:{}".format(self.url, self.timeout_s, self.ping)


class ResponseHeaders(object):
    def __init__(self, headers):
        self.headers = dict(headers)

    def get(self, field):
        return self.headers.get(field)

    def is_headers_empty(self):
        return len(self.headers) == 0

    def get_content_type(self):
        if "Content-Type" in self.headers:
            return self.headers["Content-Type"]
        if "content-type" in self.headers:
            return self.headers["content-type"]

    def get_content_type_keys(self):
        content_type = self.get_content_type()
        if content_type:
            semicolon = content_type.find(";")
            if semicolon >= 0:
                content_type = content_type[:semicolon]
            content_type = content_type.replace("+", "/")
            return content_type.split("/")

    def get_last_modified(self):
        date = None

        if "Last-Modified" in self.headers:
            date = self.headers["Last-Modified"]
        if "last-modified" in self.headers:
            date = self.headers["last-modified"]

        if date:
            return date_str_to_date(str(date))

    def get_clean_headers(self):
        self.headers["Content-Type"] = self.get_content_type()
        self.headers["Content-Length"] = self.get_content_length()
        self.headers["Last-Modified"] = self.get_last_modified()
        self.headers["Charset"] = self.get_content_type_charset()

        return self.headers

    def get_encoding(self):
        if not self.is_headers_empty():
            charset = self.get_content_type_charset()
            if charset:
                return charset

    def get_default_encoding(self):
        return "utf-8"

    def get_content_type_charset(self):
        content = self.get_content_type()
        if not content:
            return

        elements = content.split(";")
        for element in elements:
            wh = element.lower().find("charset")
            if wh >= 0:
                charset_elements = element.split("=")
                if len(charset_elements) > 1:
                    charset = charset_elements[1]

                    if charset.startswith('"') or charset.startswith("'"):
                        return charset[1:-1]
                    else:
                        return charset

    def is_content_html(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("html") >= 0:
            return True

    def is_content_image(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("image") >= 0:
            return True

    def is_content_rss(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("rss") >= 0:
            return True
        if content.lower().find("xml") >= 0:
            return True

    def is_content_json(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("json") >= 0:
            return True

    def get_content_length(self):
        content_len = None
        if "content-length" in self.headers:
            content_len = self.headers["content-length"]
        if "Content-Length" in self.headers:
            content_len = self.headers["Content-Length"]

        if content_len:
            return int(content_len)

    def get_redirect_url(self):
        if "Location" in self.headers and self.headers["Location"]:
            return self.headers["Location"]

def get_request_to_bytes(request, script):
    total_bytes = bytearray()

    bytes1 = string_to_command("PageRequestObject.__init__", "OK")
    bytes2 = string_to_command("PageRequestObject.url", request.url)
    bytes3 = string_to_command("PageRequestObject.timeout", str(request.timeout_s))
    if request.user_agent != None:
        bytes4 = string_to_command(
            "PageRequestObject.user_agent", str(request.user_agent)
        )
    else:
        bytes4 = bytearray()
    if request.request_headers != None:
        bytes5 = string_to_command(
            "PageRequestObject.request_headers", json.dumps(request.request_headers)
        )
    else:
        bytes5 = bytearray()

    bytes6 = string_to_command("PageRequestObject.ssl_verify", str(request.ssl_verify))
    bytes7 = string_to_command("PageRequestObject.script", script)

    bytes8 = string_to_command("PageRequestObject.__del__", "OK")

    total_bytes.extend(bytes1)
    total_bytes.extend(bytes2)
    total_bytes.extend(bytes3)
    total_bytes.extend(bytes4)
    total_bytes.extend(bytes5)
    total_bytes.extend(bytes6)
    total_bytes.extend(bytes7)
    total_bytes.extend(bytes8)

    return total_bytes
