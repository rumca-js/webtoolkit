"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

from utils.dateutils import DateUtils

from webtoolkit import (
   CrawlerInterface,
)

from tests.fakeinternetdata import TestResponseObject


class MockRequestCounter(object):
    mock_page_requests = 0
    request_history = []

    def requested(url, info=None, crawler_data=None):
        """
        Info can be a dict
        """
        MockRequestCounter.request_history.append({"url": url, "info" : info, "crawler_data": crawler_data})
        MockRequestCounter.mock_page_requests += 1

        print(f"Requested: {url}")
        #MockRequestCounter.debug_lines()

    def reset():
        MockRequestCounter.mock_page_requests = 0
        MockRequestCounter.request_history = []

    def debug_lines():
        stack_lines = traceback.format_stack()
        stack_string = "\n".join(stack_lines)
        print(stack_string)


class MockUrl(object):
    def __init__(self, url=None, settings=None, url_builder=None):
        self.url = url
        self.settings = settings
        self.url_builder = url_builder

    def get_init_settings(self):
        return MockCrawler.get_default_crawler(self.url)

    def get_handlers():
        return []

    def get_type():
        pass

    def get_contents(self):
        return ""

    def get_response(self):
        headers = {}
        timeout_s = 20
        self.response = TestResponseObject(self.url, headers, timeout_s)
        return self.response

    def get_streams(self):
        pass

    def ping(self, timeout_s=20, user_agent=None):
        return True

    def get_urls(self):
        return []

    def get_title(self):
        pass

    def get_description(self):
        pass

    def get_language(self):
        pass

    def get_thumbnail(self):
        pass

    def get_author(self):
        pass

    def get_album(self):
        pass

    def get_tags(self):
        pass

    def get_date_published(self):
        pass

    def get_status_code(self):
        return 200


class MockCrawler(CrawlerInterface):

    def run(self):
        request = self.request

        if self.settings:
            print("FakeInternet:Url:{} Crawler:{}".format(request.url, self.settings["name"]))
        else:
            print("FakeInternet:Url:{}".format(self.request.url))

        MockRequestCounter.requested(request.url, crawler_data=self.settings)

        self.response = TestResponseObject(request.url, request.headers, request.timeout_s)

        return self.response

    def is_valid(self):
        return True

    def get_default_crawler(url):
        data = {}
        data["name"] = "MockCrawler"
        data["crawler"] = MockCrawler(url = url)
        data["settings"] = {"timeout_s" : 20}

        return data


