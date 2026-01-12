"""
This module provides mocks
"""

from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    BaseUrl,
    CrawlerInterface,
    PageRequestObject,
    PageResponseObject,
    YouTubeVideoHandler,
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


class YtdlpCrawlerMock(CrawlerInterface):

    def run(self):
        MockRequestCounter.requested(self.request.url, crawler_data=self.request)

        h = YouTubeVideoHandler(self.request.url)
        code = h.get_video_code()

        yt_text = ""
        status_code = 200

        if code == "1234":
            yt_text = """{"_filename" : "1234 test file name",
            "title" : "1234 test title",
            "description" : "1234 test description",
            "channel_url" : "https://youtube.com/channel/1234-channel",
            "channel" : "1234-channel",
            "channel_follower_count" : 5,
            "id" : "1234-id",
            "channel_id" : "1234-channel-id",
            "thumbnail" : "https://youtube.com/files/1234-thumbnail.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "like_count" : 5,
            "live_status" : "False"
            }""".replace(
                "${date}", self.get_now()
            )
        if code == "666":
            status_code = 401
        if code == "555555":
            yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "like_count" : 5,
            "live_status" : "True"
            }""".replace(
                "${date}", self.get_now()
            )
        if code == "archived":
            yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "20231113",
            "view_count" : "2",
            "like_count" : 5,
            "live_status" : "False"
            }""".replace(
                "${date}", self.get_now()
            )
        else:
            yt_text = """{"_filename" : "test.txt",
            "title" : "test.txt",
            "description" : "test.txt",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "like_count" : 5,
            "live_status" : "False"
            }""".replace(
                "${date}", self.get_now()
            )

        headers = {}
        headers["Content-Type"] = "text/json"

        self.response = PageResponseObject(
            url=self.request.url,
            text=yt_text,
            status_code=status_code,
            encoding="utf-8",
            headers=headers,
            binary=None,
            request_url=self.request.url,
        )

        return self.response

    def is_valid(self):
        return True

    def get_now(self):
        """
        format 20231113
        """
        date = DateUtils.get_datetime_now_utc()
        tuple = DateUtils.get_date_tuple(date)

        return str(tuple[0]) + str(tuple[1]) + str(tuple[2])
