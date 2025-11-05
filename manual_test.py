import requests

from webtoolkit import (
   YouTubeChannelHandler,
   YouTubeVideoHandler,
   OdyseeChannelHandler,
   OdyseeVideoHandler,
   PageRequestObject,
   HttpPageHandler,
   CrawlerInterface,
   RequestsCrawler,
)


class UrlBuilder(HttpPageHandler):
    def __init__(self, url=None, request=None,url_builder=None, contents=None):
        if request and request.crawler_type is None:
            request.crawler_name = "RequestsCrawler"
            request.crawler_type = RequestsCrawler(request.url)

        super().__init__(url=url, request=request, url_builder = url_builder, contents=contents)


def print_handler(handler):
    print("Title: {}".format(handler.get_title()))
    print("Description: {}".format(handler.get_description()))
    print("Thumbnail: {}".format(handler.get_thumbnail()))


def run_with_handler(test_url, handler):
    print("Running {}".format(test_url))
    request = PageRequestObject(url=test_url)
    request.crawler_name = "RequestsCrawler"
    request.crawler_type = RequestsCrawler(request.url)
    handler = handler(request=request, url_builder=UrlBuilder)
    response = handler.get_response()

    #print(response)
    #print_handler(handler)

    return response, handler


def test_vanilla_google():
    test_url = "https://www.google.com"
    response, handler = run_with_handler(test_url, HttpPageHandler)


def test_youtube_channel_by_rss():
    test_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    entries_len = len(list(handler.get_entries()))
    if entries_len == 0:
        print("---------------> Entries len is 0---------------")


def test_youtube_channel_by_channel():
    test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    entries_len = len(list(handler.get_entries()))
    if entries_len == 0:
        print("---------------> Entries len is 0---------------")


def test_youtube_channel_by_handle():
    test_url = "https://www.youtube.com/@LinusTechTips"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)

    entries_len = len(list(handler.get_entries()))
    if entries_len == 0:
        print("---------------> Entries len is 0---------------")


def test_youtube_video():
    test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
    return run_with_handler(test_url, YouTubeVideoHandler)


def test_odysee_channel():
    test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
    response, handler = run_with_handler(test_url, OdyseeChannelHandler)

    entries_len = len(list(handler.get_entries()))
    if entries_len == 0:
        print("---------------> Entries len is 0---------------")


def test_odysee_video():
    test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"

    return run_with_handler(test_url, OdyseeVideoHandler)


def main():
    #print("------------------------")
    #test_vanilla_google()
    print("------------------------")
    test_youtube_channel_by_rss()
    print("------------------------")
    test_youtube_channel_by_channel()
    #print("------------------------")
    #test_youtube_video()
    print("------------------------")
    test_youtube_channel_by_handle()
    #print("------------------------")
    #test_odysee_video()
    print("------------------------")
    test_odysee_channel()


main()

