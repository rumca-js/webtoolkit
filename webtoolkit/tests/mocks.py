"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    CrawlerInterface,
    PageRequestObject,
)

from webtoolkit.tests.fakeresponse import TestResponseObject


class MockRequestCounter(object):
    mock_page_requests = 0
    request_history = []

    def requested(url, info=None, crawler_data=None):
        """
        Info can be a dict
        """
        MockRequestCounter.request_history.append(
            {"url": url, "info": info, "crawler_data": crawler_data}
        )
        MockRequestCounter.mock_page_requests += 1

        print(f"Requested: {url}")
        # MockRequestCounter.debug_lines()

    def reset():
        MockRequestCounter.mock_page_requests = 0
        MockRequestCounter.request_history = []

    def debug_lines():
        stack_lines = traceback.format_stack()
        stack_string = "\n".join(stack_lines)
        print(stack_string)


class MockUrl(object):
    def __init__(self, url=None, request=None, url_builder=None):
        self.url = url
        self.request = request
        self.response = None
        self.url_builder = url_builder

    def get_init_settings(self):
        return MockCrawler.get_default_crawler(self.url)

    def get_init_request(self):
        request = PageRequestObject(self.url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url=self.url)
        return request

    def get_handlers():
        return []

    def get_type():
        pass

    def get_contents(self):
        response = self.get_response()
        return response.get_text()

    def get_response(self):
        if self.response:
            return self.response

        headers = {}
        timeout_s = 20
        self.response = TestResponseObject(self.url, headers, timeout_s)

        MockRequestCounter.requested(self.url, crawler_data=self.request)

        return self.response

    def get_streams(self):
        return []

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

    def get_properties(self):
        return {}


class MockCrawler(CrawlerInterface):

    def run(self):
        request = self.request

        if self.request:
            print(
                "FakeInternet:Url:{} Crawler:{}".format(
                    request.url, self.request.crawler_name
                )
            )
        else:
            print("FakeInternet:Url:{}".format(self.request.url))

        MockRequestCounter.requested(request.url, crawler_data=self.request)

        self.response = TestResponseObject(
            request.url, request.request_headers, request.timeout_s
        )

        return self.response

    def is_valid(self):
        return True

    def get_default_crawler(url):
        data = {}
        data["name"] = "MockCrawler"
        data["crawler"] = MockCrawler(url=url)
        data["settings"] = {"timeout_s": 20}

        return data
