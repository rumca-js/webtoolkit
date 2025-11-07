"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    BaseUrl,
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


class MockUrl(BaseUrl):

    def __init__(self, url=None, request=None, url_builder=None):
        if url_builder is None:
            url_builder = MockUrl
        super().__init__(url=url, request=request, url_builder=url_builder)

    def get_request_for_url(self, url):
        request = PageRequestObject(url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url)

        return request

    def get_request_for_request(self, request):
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(request.url)

        return request

    def get_init_request(self):
        request = PageRequestObject(self.url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url=self.url)
        return request


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
