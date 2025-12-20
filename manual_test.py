"""
Set of manual, real world tests
"""
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
from webtoolkit.webconfig import WebConfig


def print_bar():
    print("------------------------")


def run_with_base_url(test_url):
    print("Running {} with BaseUrl".format(test_url))

    url = BaseUrl(url=test_url)
    response = url.get_response()
    handler = url.get_handler()

    if response is None:
        print("Missing response!")
        return response, handler
    if response.is_invalid():
        print("Invalid response")
        return response, handler
    if response.get_text() is None:
        print("No text in response")
        return response, handler

    if handler.get_title() is None:
        print("No title in url")
        return response, handler

    if not handler.get_hash():
        print("No hash")

    if not handler.get_body_hash():
        print("No body hash")

    entries_len = len(list(handler.get_entries()))
    print(f"Entries: {entries_len}")

    streams_len = len(list(handler.get_streams()))
    print(f"Streams: {streams_len}")

    properties = url.get_social_properties()
    print(f"Social properties: {properties}")

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
    return response, handler


def test_baseurl__youtube_video():
    test_url = "https://www.youtube.com/watch?v=9yanqmc01ck"
    response, handler = run_with_base_url(test_url)
    if handler:
        print("Title: {}".format(handler.get_title()))
    return response, handler


def test_baseurl__youtube_channel_by_id():
    test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
    response, handler = run_with_base_url(test_url)
    if handler:
        print("Title: {}".format(handler.get_title()))
        print("Feeds: {}".format(handler.get_feeds()))
    return response, handler


def test_baseurl__youtube_channel_by_handle():
    test_url = "https://www.youtube.com/@LinusTechTips"
    response, handler = run_with_base_url(test_url)
    if handler:
        print("Title: {}".format(handler.get_title()))
    return response, handler


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

    all_properties = url.get_all_properties()

    remote_url = RemoteUrl(all_properties=all_properties)
    remote_response = remote_url.get_response()

    if not remote_response.is_valid():
        print("Remote response is not valid")
        return

    if not remote_url.get_title():
        print("No title")
        return

    if not remote_url.get_hash():
        print("No hash")

    if not remote_url.get_body_hash():
        print("No body hash")

    remote_responses = remote_url.get_responses()
    if not remote_responses:
        print("No responses")
        return

    print_bar()


def test_baseurl__is_allowed():
    test_url = "https://www.youtube.com/watch?v=Vzgimftolys&pp=ygUPbGludXMgdGVjaCB0aXBz"

    print("Running RemoteUrl test {} with handler".format(test_url))

    url = BaseUrl(url=test_url)
    print("Robots allowed? {}".format(url.is_allowed()))


def main():
    #WebConfig.use_print_logging()

    print_bar()
    test_baseurl__vanilla_google()
    print_bar()
    test_baseurl__youtube_video()
    print_bar()
    test_baseurl__youtube_channel_by_id()
    print_bar()
    test_baseurl__youtube_channel_by_handle()
    print_bar()
    test_baseurl__odysee_video()
    print_bar()
    test_baseurl__odysee_channel()
    print_bar()
    test_baseurl__github()
    print_bar()
    test_baseurl__reddit__channel()
    print_bar()
    test_baseurl__reddit__news()
    print_bar()

    test_baseurl__remote_url()
    print_bar()
    test_baseurl__is_allowed()
    print_bar()


main()
