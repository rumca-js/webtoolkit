import requests

from webtoolkit import (
   BaseUrl,
   RemoteUrl,
   YouTubeChannelHandler,
   YouTubeVideoHandler,
   OdyseeChannelHandler,
   OdyseeVideoHandler,
   PageRequestObject,
   HttpPageHandler,
   CrawlerInterface,
   RequestsCrawler,
)


def print_bar():
    print("------------------------")


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
    print("Running {} with handler {}".format(test_url, handler.__name__))
    request = PageRequestObject(url=test_url)
    request.crawler_name = "RequestsCrawler"
    request.crawler_type = RequestsCrawler(request.url)
    handler = handler(request=request, url_builder=UrlBuilder)
    response = handler.get_response()

    if response is None:
        print("Missing response!")
        return
    if response.is_invalid():
        print("Invalid response")
        return
    if response.get_text() is None:
        print("No text in response")
        return

    entries_len = len(list(handler.get_entries()))
    print(f"Entries: {entries_len}")

    streams_len = len(list(handler.get_streams()))
    print(f"Streams: {streams_len}")

    #print(response)
    #print_handler(handler)

    print_bar()

    return response, handler


def run_with_base_url(test_url):
    print("Running {} with BaseUrl".format(test_url))

    url = BaseUrl(url=test_url)
    response = url.get_response()
    handler = url.get_handler()

    if response is None:
        print("Missing response!")
        return
    if response.is_invalid():
        print("Invalid response")
        return
    if response.get_text() is None:
        print("No text in response")
        return

    if handler.get_title() is None:
        print("No title in url")
        return

    entries_len = len(list(handler.get_entries()))
    print(f"Entries: {entries_len}")

    streams_len = len(list(handler.get_streams()))
    print(f"Streams: {streams_len}")

    properties = url.get_social_properties()
    print(f"Social properties: {properties}")

    print_bar()

    return response, handler


def test_handler_vanilla_google():
    test_url = "https://www.google.com"
    response, handler = run_with_handler(test_url, HttpPageHandler)
    return response, handler


def test_handler_youtube_channel_by_rss():
    test_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)



def test_handler_youtube_channel_by_channel():
    test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)


def test_handler_youtube_channel_by_handle():
    test_url = "https://www.youtube.com/@LinusTechTips"
    response, handler = run_with_handler(test_url, YouTubeChannelHandler)


def test_handler_youtube_video():
    test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
    return run_with_handler(test_url, YouTubeVideoHandler)


def test_handler_odysee_channel():
    test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
    response, handler = run_with_handler(test_url, OdyseeChannelHandler)


def test_handler_odysee_video():
    test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"

    return run_with_handler(test_url, OdyseeVideoHandler)


def test_baseurl__vanilla_google():
    test_url = "https://www.google.com"
    response,handler = run_with_base_url(test_url)
    return response,handler


def test_baseurl__youtube_video():
    test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
    return run_with_base_url(test_url)


def test_baseurl__youtube_channel():
    test_url = "https://www.youtube.com/@LinusTechTips"
    response, handler = run_with_base_url(test_url)


def test_baseurl__odysee_channel():
    test_url = "https://odysee.com/$/rss/@BrodieRobertson:5"
    response, handler = run_with_base_url(test_url)


def test_baseurl__odysee_video():
    test_url = "https://odysee.com/servo-browser-finally-hits-a-major:24fc604b8d282b226091928dda97eb0099ab2f05"
    return run_with_base_url(test_url)


def test_baseurl__github():
    test_url = "https://github.com/rumca-js/crawler-buddy"
    return run_with_base_url(test_url)


def test_baseurl__reddit__channel():
    test_url = "https://www.reddit.com/r/wizardposting"
    return run_with_base_url(test_url)


def test_baseurl__reddit__news():
    test_url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/"
    return run_with_base_url(test_url)


def test_baseurl__remote_url():
    test_url = "https://www.google.com"

    print("Running RemoteUrl test {} with handler".format(test_url))

    url = BaseUrl(url=test_url)
    response = url.get_response()

    all_properties = url.get_properties(full=True)

    remote_url = RemoteUrl(all_properties=all_properties)
    remote_response = remote_url.get_response()

    if not remote_response.is_valid():
        print("Remote response is not valid")
        return

    if not remote_url.get_title():
        print("No title")
        return

    remote_responses = remote_url.get_responses()
    if not remote_responses:
        print("No responses")
        return

    print_bar()


def main():
    test_handler_vanilla_google()
    test_handler_youtube_channel_by_rss()
    test_handler_youtube_channel_by_channel()
    test_handler_youtube_video()
    test_handler_youtube_channel_by_handle()
    test_handler_odysee_video()
    test_handler_odysee_channel()

    test_baseurl__vanilla_google()
    test_baseurl__youtube_video()
    test_baseurl__youtube_channel()
    test_baseurl__odysee_video()
    test_baseurl__odysee_channel()
    test_baseurl__github()
    test_baseurl__reddit__channel()
    test_baseurl__reddit__news()

    test_baseurl__remote_url()


main()
