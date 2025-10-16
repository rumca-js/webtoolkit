"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

from utils.dateutils import DateUtils
from webtoolkit import YouTubeJsonHandler, YouTubeChannelHandler


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


class YouTubeJsonHandlerMock(YouTubeJsonHandler):
    def __init__(self, url, settings=None, url_builder=None):
        super().__init__(url, settings=settings, url_builder=url_builder)

    def download_details_youtube(self):
        MockRequestCounter.requested(self.url)

        if self.get_video_code() == "1234":
            self.yt_text = """{"_filename" : "1234 test file name",
            "title" : "1234 test title",
            "description" : "1234 test description",
            "channel_url" : "https://youtube.com/channel/1234-channel",
            "channel" : "1234-channel",
            "id" : "1234-id",
            "channel_id" : "1234-channel-id",
            "thumbnail" : "https://youtube.com/files/1234-thumbnail.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())
        if self.get_video_code() == "666":
            pass
        if self.get_video_code() == "555555":
            self.yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "True"
            }""".replace("${date}", self.get_now())
        if self.get_video_code() == "archived":
            self.yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "20231113",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())
        else:
            self.yt_text = """{"_filename" : "test.txt",
            "title" : "test.txt",
            "description" : "test.txt",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())

        if self.get_video_code() == "666":
            return False
        else:
            return self.load_details_youtube()

    def get_now(self):
        """
        format 20231113
        """
        date = DateUtils.get_datetime_now_utc()
        tuple = DateUtils.get_date_tuple(date)

        return str(tuple[0]) + str(tuple[1]) + str(tuple[2])


class YouTubeChannelHandlerMock(YouTubeChannelHandler):
    def input2code_handle(self, url):
        return "UUUUUUUUUUUUUUUU"
