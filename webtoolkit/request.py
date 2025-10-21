"""
"""

import html
import json

from .webtools import date_str_to_date



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
