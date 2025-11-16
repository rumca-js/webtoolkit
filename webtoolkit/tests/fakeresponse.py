"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

import logging
import unittest
import traceback

from webtoolkit.utils.dateutils import DateUtils

from webtoolkit import (
    calculate_hash,
    json_encode_field,
    json_decode_field,
    response_to_json,
    PageResponseObject,
    ResponseHeaders,
    HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_USER_AGENT,
)

from webtoolkit.tests.fakeinternetcontents import (
    webpage_with_real_rss_links,
    webpage_simple_rss_page,
    webpage_old_pubdate_rss,
    webpage_no_pubdate_rss,
    webpage_html_favicon,
    webpage_with_rss_link_rss_contents,
    webpage_html_casinos,
    webpage_html_canonical_1,
    webpage_with_date_published,
)
from webtoolkit.tests.fake.geekwirecom import (
    geekwire_feed,
)
from webtoolkit.tests.fake.youtube import (
    youtube_robots_txt,
    youtube_sitemap_sitemaps,
    youtube_sitemap_product,
    webpage_youtube_airpano_feed,
    webpage_samtime_odysee,
    webpage_samtime_youtube_rss,
    youtube_channel_html_linus_tech_tips,
    youtube_channel_rss_linus_tech_tips,
)
from webtoolkit.tests.fake.robotstxtcom import (
    robots_txt_example_com_robots,
)
from webtoolkit.tests.fake.codeproject import (
    webpage_code_project_rss,
)
from webtoolkit.tests.fake.opmlfile import (
    opml_file,
)
from webtoolkit.tests.fake.hackernews import (
    webpage_hackernews_rss,
    hacker_news_item,
)
from webtoolkit.tests.fake.warhammercommunity import (
    warhammer_community_rss,
)
from webtoolkit.tests.fake.thehill import (
    thehill_rss,
)
from webtoolkit.tests.fake.reddit import (
    reddit_rss_text,
    reddit_entry_json,
    reddit_subreddit_json,
)
from webtoolkit.tests.fake.githubcom import (
    github_json,
)
from webtoolkit.tests.fake.returndislike import (
    return_dislike_json,
)
from webtoolkit.tests.fake.firebog import (
    firebog_adguard_list,
    firebog_w3kbl_list,
    firebog_tick_lists,
    firebog_malware,
)
from webtoolkit.tests.fake.instance import (
    instance_entries_json,
    instance_sources_json_empty,
    instance_entries_json_empty,
    instance_entries_source_100_json,
    instance_source_100_url,
    instance_source_100_json,
    instance_source_101_json,
    instance_source_102_json,
    instance_source_103_json,
    instance_source_104_json,
    instance_source_105_json,
    instance_sources_page_1,
    instance_sources_page_2,
)


class PageBuilder(object):
    def __init__(self):
        self.charset = "UTF-8"
        self.title = None
        self.title_meta = None
        self.description_meta = None
        self.author = None
        self.keywords = None
        self.og_title = None
        self.og_description = None
        self.body_text = ""

    def build_contents(self):
        html = self.build_html()
        html = self.build_head(html)
        html = self.build_body(html)
        return html

    def build_html(self):
        return """
        <html>
        ${HEAD}
        ${BODY}
        </html>"""

    def build_body(self, html):
        html = html.replace("${BODY}", "<body>{}</body>".format(self.body_text))
        return html

    def build_head(self, html):
        # fmt: off

        meta_info = ""
        if self.title:
            meta_info += '<title>{}</title>\n'.format(self.title)
        if self.title_meta:
            meta_info += '<meta name="title" content="{}">\n'.format(self.title_meta)
        if self.description_meta:
            meta_info += '<meta name="description" content="{}">\n'.format(self.description_meta)
        if self.author:
            meta_info += '<meta name="author" content="{}">\n'.format(self.author)
        if self.keywords:
            meta_info += '<meta name="keywords" content="{}">\n'.format(self.keywords)
        if self.og_title:
            meta_info += '<meta property=”og:title” content="{}">\n'.format(self.og_title)
        if self.og_description:
            meta_info += '<meta property=”og:description” content="{}">\n'.format(self.og_description)

        # fmt: on

        html = html.replace("${HEAD}", "<head>{}</head>".format(meta_info))
        return html


class TestResponseObject(PageResponseObject):
    """
    TODO maybe we should inherit from webtools/PageResponseObject?
    """

    def __init__(self, url, headers, timeout):
        super().__init__(url=url, headers=headers)

        self.status_code = 200
        self.errors = []
        self.crawl_time_s = 10

        self.url = url
        self.request_url = url

        encoding = "utf-8"
        self.apparent_encoding = encoding
        self.encoding = encoding

        self.set_headers(url)
        self.set_status(url)
        self.set_text(url)
        self.set_binary(url)

    def set_headers(self, url):
        headers = {}
        if url == "https://page-with-last-modified-header.com":
            headers["Last-Modified"] = "Wed, 03 Apr 2024 09:39:30 GMT"

        elif url == "https://page-with-rss-link.com/feed":
            headers["Content-Type"] = "application/+rss"

        elif url.startswith("https://warhammer-community.com/feed"):
            headers["Content-Type"] = "application/+rss"

        elif url.startswith("https://thehill.com/feed"):
            headers["Content-Type"] = "application/+rss"

        elif url.find("instance.com") >= 0 and url.find("json") >= 0:
            headers["Content-Type"] = "json"

        elif url.startswith("https://binary") and url.find("jpg") >= 0:
            headers["Content-Type"] = "image/jpg"

        elif url.startswith("https://image"):
            headers["Content-Type"] = "image/jpg"

        elif url.startswith("https://audio"):
            headers["Content-Type"] = "audio/midi"

        elif url.startswith("https://video"):
            headers["Content-Type"] = "video/mp4"

        elif url == "https://rss-page-with-broken-content-type.com/feed":
            headers["Content-Type"] = "text/html"

        self.headers = ResponseHeaders(headers=headers)

    def set_status(self, url):
        if url.startswith("https://www.youtube.com/watch?v=666"):
            self.status_code = 500

        elif url == "https://invalid.rsspage.com/rss.xml":
            self.status_code = 500

        elif url == "https://page-with-http-status-500.com":
            self.status_code = 500

        elif url == "https://page-with-http-status-400.com":
            self.status_code = 400

        elif url == "https://page-with-http-status-300.com":
            self.status_code = 300

        elif url == "https://page-with-http-status-200.com":
            self.status_code = 200

        elif url == "https://page-with-http-status-100.com":
            self.status_code = 100

        elif url == "http://page-with-http-status-500.com":
            self.status_code = 500

        elif url == "http://page-with-http-status-400.com":
            self.status_code = 400

        elif url == "http://page-with-http-status-300.com":
            self.status_code = 300

        elif url == "http://page-with-http-status-200.com":
            self.status_code = 200

        elif url == "http://page-with-http-status-100.com":
            self.status_code = 100

        elif url == "https://page-with-https-status-200-http-status-500.com":
            self.status_code = 200

        elif url == "http://page-with-https-status-200-http-status-500.com":
            self.status_code = 500

        elif url == "https://page-with-https-status-500-http-status-200.com":
            self.status_code = 500

        elif url == "http://page-with-https-status-500-http-status-200.com":
            self.status_code = 200

        elif url == "https://page-with-http-status-500.com/robots.txt":
            self.status_code = 500

    def set_text(self, url):
        if url.startswith("https://binary"):
            self.text = None
            return
        elif url.startswith("https://image"):
            self.text = None
            return
        elif url.startswith("https://audio"):
            self.text = None
            return
        elif url.startswith("https://video"):
            self.text = None
            return

        text = self.get_text_for_url(url)
        self.text = text

    def get_text_for_url(self, url):
        if url.startswith("https://www.youtube.com/channel/"):
            return self.get_contents_youtube_channel(url)

        if url.startswith("https://youtube.com/channel/"):
            return self.get_contents_youtube_channel(url)

        if url.startswith("https://www.youtube.com/watch?v=666"):
            self.status_code = 500

        if url.startswith("https://www.youtube.com/watch?v=666"):
            return webpage_no_pubdate_rss

        if url.startswith("https://www.youtube.com/watch?v=date_published"):
            return webpage_with_date_published

        if url.startswith(
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        ):
            return youtube_channel_rss_linus_tech_tips

        if url.startswith("https://www.youtube.com/feeds"):
            return webpage_samtime_youtube_rss

        if url == "https://www.youtube.com/robots.txt":
            return youtube_robots_txt

        if url == "https://www.youtube.com/sitemaps/sitemap.xml":
            return youtube_sitemap_sitemaps

        if url == "https://www.youtube.com/product/sitemap.xml":
            return youtube_sitemap_product

        if url.startswith("https://returnyoutubedislikeapi.com/votes?videoId=666"):
            return ""

        if url.startswith("https://returnyoutubedislikeapi.com/votes?videoId"):
            return return_dislike_json

        if url.startswith("https://odysee.com/$/rss"):
            return webpage_samtime_youtube_rss

        if url.startswith("https://odysee.com/"):
            return youtube_channel_html_linus_tech_tips

        if url == "https://rss-page-with-broken-content-type.com/feed":
            return youtube_channel_html_linus_tech_tips

        if url.startswith("https://www.geekwire.com/feed"):
            return geekwire_feed

        if url.startswith("https://www.rss-in-html.com/feed"):
            return geekwire_feed

        if url == "https://www.reddit.com/r/InternetIsBeautiful/.json":
            return reddit_subreddit_json

        if url.startswith("https://www.reddit.com/r/") and url.endswith(".rss"):
            return reddit_rss_text

        if url.startswith("https://www.reddit.com") and url.endswith(".json"):
            return reddit_entry_json

        if url.startswith("https://api.github.com"):
            return github_json

        if url.startswith("https://hnrss.org"):
            return webpage_hackernews_rss

        if url.startswith("https://news.ycombinator.com/item?id="):
            return webpage_samtime_youtube_rss

        if url.startswith("https://hacker-news.firebaseio.com/v0/item/"):
            return hacker_news_item

        if url.startswith("https://warhammer-community.com/feed"):
            return warhammer_community_rss

        if url.startswith("https://thehill.com/feed"):
            return thehill_rss

        if url.startswith("https://isocpp.org/blog/rss/category/news"):
            return webpage_samtime_youtube_rss

        if url.startswith("https://cppcast.com/feed.rss"):
            return webpage_samtime_youtube_rss

        elif url == "https://multiple-favicons.com/page.html":
            return webpage_html_favicon

        elif url == "https://rsspage.com/rss.xml":
            return webpage_samtime_odysee

        elif url == "https://opml-file-example.com/ompl.xml":
            return opml_file

        elif url == "https://invalid.rsspage.com/rss.xml":
            return ""

        elif url == "https://simple-rss-page.com/rss.xml":
            return webpage_simple_rss_page

        elif url == "https://empty-page.com":
            return ""

        elif url == "https://www.codeproject.com/WebServices/NewsRSS.aspx":
            return webpage_code_project_rss

        elif url.find("https://api.github.com/repos") >= 0:
            return """{"stargazers_count" : 5}"""

        elif url.find("https://www.reddit.com/") >= 0 and url.endswith("json"):
            return """{"upvote_ratio" : 5}"""

        elif url.find("https://returnyoutubedislikeapi.com/votes") >= 0:
            return """{"likes" : 5,
                       "dislikes" : 5,
                       "viewCount" : 5,
                       "rating": 5}"""

        elif url == "https://page-with-two-links.com":
            b = PageBuilder()
            b.title_meta = "Page title"
            b.description_meta = "Page description"
            b.og_title = "Page og_title"
            b.og_description = "Page og_description"
            b.body_text = """<a href="https://link1.com">Link1</a>
                     <a href="https://link2.com">Link2</a>"""

            return b.build_contents()

        elif url == "https://page-with-rss-link.com":
            return """
              <html>
                 <head>
                     <link type="application/rss+xml"  href="https://page-with-rss-link.com/feed"/>
                 </head>
                 <body>
                    no body
                 </body>
             </html>
             """

        elif url == "https://page-with-rss-link.com/feed":
            return webpage_with_rss_link_rss_contents

        elif url == "https://page-with-canonical-link.com":
            return webpage_html_canonical_1

        elif url == "https://page-without-canonical-link.com":
            return webpage_with_real_rss_links

        elif url == "https://slot-casino-page.com":
            return webpage_html_casinos

        elif url == "https://page-with-real-rss-link.com":
            return webpage_with_real_rss_links

        elif url.startswith("https://instance.com/apps/rsshistory"):
            return self.get_contents_instance(url)

        elif url == "https://title-in-head.com":
            b = PageBuilder()
            b.title = "Page title"
            b.description_meta = "Page description"
            b.og_description = "Page og_description"
            b.body_text = """Something in the way"""
            return b.build_contents()

        elif url == "https://no-props-page.com":
            b = PageBuilder()
            b.title = None
            b.description_meta = None
            b.og_description = None
            b.body_text = """Something in the way"""
            return b.build_contents()

        elif url == "https://title-in-meta.com":
            b = PageBuilder()
            b.title = "Page title"
            b.description_meta = "Page description"
            b.og_description = "Page og_description"
            b.body_text = """Something in the way"""
            return b.build_contents()

        elif url == "https://title-in-og.com":
            b = PageBuilder()
            b.og_title = "Page title"
            b.description_meta = "Page description"
            b.og_description = "Page og_description"
            b.body_text = """Something in the way"""
            return b.build_contents()

        elif url == "https://linkedin.com":
            b = PageBuilder()
            b.title_meta = "Https LinkedIn Page title"
            b.description_meta = "LinkedIn Page description"
            b.og_title = "Https LinkedIn Page og:title"
            b.og_description = "LinkedIn Page og:description"
            b.body_text = """LinkedIn body"""
            return b.build_contents()

        elif url == "http://linkedin.com":
            b = PageBuilder()
            b.title_meta = "Http LinkedIn Page title"
            b.description_meta = "LinkedIn Page description"
            b.og_title = "Http LinkedIn Page og:title"
            b.og_description = "LinkedIn Page og:description"
            b.body_text = """LinkedIn body"""
            return b.build_contents()

        elif url == "https://www.linkedin.com":
            b = PageBuilder()
            b.title_meta = "Https www LinkedIn Page title"
            b.description_meta = "LinkedIn Page description"
            b.og_title = "Https LinkedIn Page og:title"
            b.og_description = "LinkedIn Page og:description"
            b.body_text = """LinkedIn body"""
            return b.build_contents()

        elif url == "http://www.linkedin.com":
            b = PageBuilder()
            b.title_meta = "Http www LinkedIn Page title"
            b.description_meta = "LinkedIn Page description"
            b.og_title = "Http www LinkedIn Page og:title"
            b.og_description = "LinkedIn Page og:description"
            b.body_text = """LinkedIn body"""
            return b.build_contents()

        elif url == "https://page-with-last-modified-header.com":
            return webpage_html_favicon

        elif url == "https://v.firebog.net/hosts/AdguardDNS.txt":
            return firebog_adguard_list

        elif url == "https://v.firebog.net/hosts/static/w3kbl.txt":
            return firebog_w3kbl_list

        elif url == "https://v.firebog.net/hosts/lists.php?type=tick":
            return firebog_tick_lists

        elif url == "https://v.firebog.net/hosts/RPiList-Malware.txt":
            return firebog_malware

        elif url == "https://robots-txt.com/robots.txt":
            return robots_txt_example_com_robots

        elif url.endswith("robots.txt"):
            return """  """

        elif url.endswith("sitemap.xml"):
            return """<urlset>
                      </urlset>"""

        b = PageBuilder()
        b.title_meta = "Page title"
        b.description_meta = "Page description"
        b.og_title = "Page og_title"
        b.og_description = "Page og_description"

        return b.build_contents()

    def set_binary(self, url):
        self.binary = None
        if url.startswith("https://binary"):
            text = url
            self.binary = text.encode("utf-8")
        elif url.startswith("https://image"):
            text = url
            self.binary = text.encode("utf-8")
        elif url.startswith("https://audio"):
            text = url
            self.binary = text.encode("utf-8")
        elif url.startswith("https://video"):
            text = url
            self.binary = text.encode("utf-8")

    def get_contents_youtube_channel(self, url):
        if url.startswith("https://www.youtube.com/channel"):
            return youtube_channel_html_linus_tech_tips
        elif url.startswith("https://youtube.com/channel"):
            return youtube_channel_html_linus_tech_tips
        elif url.startswith("https://www.youtube.com/@"):
            return youtube_channel_html_linus_tech_tips
        elif url.startswith("https://youtube.com/@"):
            return youtube_channel_html_linus_tech_tips
        elif url.startswith("https://www.youtube.com/user"):
            return youtube_channel_html_linus_tech_tips
        elif url.startswith("https://youtube.com/user"):
            return youtube_channel_html_linus_tech_tips

        elif url == "https://www.youtube.com/feeds/videos.xml?channel_id=2020-year-channel":
            return webpage_old_pubdate_rss

        elif url == "https://www.youtube.com/feeds/videos.xml?channel_id=nopubdate":
            return webpage_no_pubdate_rss

        elif url == "https://www.youtube.com/feeds/videos.xml?channel_id=airpano":
            return webpage_youtube_airpano_feed

        elif (
            url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        ):
            return webpage_samtime_youtube_rss

    def get_contents_instance(self, url):
        if (
            url
            == "https://instance.com/apps/rsshistory/entries-json/?query_type=recent"
        ):
            return instance_entries_json

        elif (
            url
            == "https://instance.com/apps/rsshistory/entries-json/?query_type=recent&source_title=Source100"
        ):
            return instance_entries_source_100_json

        elif (
            url
            == "https://instance.com/apps/rsshistory/entries-json/?query_type=recent&page=1"
        ):
            return """{}"""

        elif url == "https://instance.com/apps/rsshistory/source-json/100":
            return f'{{ "source": {instance_source_100_json} }}'

        elif url == "https://instance.com/apps/rsshistory/source-json/101":
            return f'{{ "source": {instance_source_101_json} }}'

        elif url == "https://instance.com/apps/rsshistory/source-json/102":
            return f'{{ "source": {instance_source_102_json} }}'

        elif url == "https://instance.com/apps/rsshistory/source-json/103":
            return f'{{ "source": {instance_source_103_json} }}'

        elif url == "https://instance.com/apps/rsshistory/source-json/104":
            return f'{{ "source": {instance_source_104_json} }}'

        elif url == "https://instance.com/apps/rsshistory/source-json/105":
            return f'{{ "source": {instance_source_105_json} }}'

        elif url == "https://instance.com/apps/rsshistory/entry-json/1912018":
            return """{}"""

        elif url == "https://instance.com/apps/rsshistory/sources-json":
            return instance_sources_page_1

        elif url == "https://instance.com/apps/rsshistory/sources-json/?page=1":
            return instance_sources_page_1

        elif url == "https://instance.com/apps/rsshistory/sources-json/?page=2":
            return instance_sources_page_2

        elif url == "https://instance.com/apps/rsshistory/sources-json/?page=3":
            return instance_sources_json_empty

        elif "/sources-json/":
            return instance_sources_json_empty

        elif "/entries-json/":
            return instance_entries_json_empty

        else:
            return """{}"""

    def __str__(self):
        has_text_data = "Yes" if self.text else "No"
        has_binary_data = "Yes" if self.binary else "No"

        return "TestResponseObject: Url:{} Status code:{} Headers:{} Text:{} Binary:{}".format(
            self.url,
            self.status_code,
            self.headers,
            has_text_data,
            has_binary_data,
        )


class FakeInternetData(object):
    def __init__(self, url):
        self.url = url
        self.properties = {
            "link": self.url,
            "title": "Title",
            "description": "Description",
            "date_published": DateUtils.get_datetime_now_iso(),
            "author": "Description",
            "language": "Language",
            "album": "Description",
            "page_rating": 80,
            "thumbnail": None,
        }

        response = TestResponseObject(self.url, {}, 15)
        self.response = response_to_json(response)

        self.text_data = "Something"
        self.binary_data = None
        self.entries = []

    def get_all_properties(self):
        data = []
        data.append({"name": "Properties", "data": self.properties})
        data.append({"name": "Request", "data": None})
        data.append({"name": "Response", "data": self.response})
        data.append({"name": "Headers", "data": {}})
        data.append({"name": "Entries", "data": self.entries})

        properties_hash = json_encode_field(calculate_hash(str(self.properties)))
        data.append({"name": "PropertiesHash", "data": properties_hash})

        data.append(
            {
                "name": "Streams",
                "data": {
                    self.url : self.response,
                },
            }
        )

        return data

    def get_getj(self, request=None, url=None):
        if request:
            url = request.url

        if url == "https://linkedin.com":
            self.properties["title"] = "Https LinkedIn Page title"
            self.properties["description"] = "Https LinkedIn Page description"
        elif url == "https://m.youtube.com/watch?v=1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif url == "https://www.youtube.com/watch?v=1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif url == "https://youtu.be/1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif url == "https://www.reddit.com/r/searchengines/":
            self.properties["feeds"] = ["https://www.reddit.com/r/searchengines/.rss"]
        elif url == "https://www.reddit.com/r/searchengines":
            self.properties["feeds"] = ["https://www.reddit.com/r/searchengines/.rss"]
        elif url == "https://www.reddit.com/r/searchengines/.rss":
            self.set_entries(10)
        elif url == "https://page-with-rss-link.com":
            self.properties["title"] = "Page with RSS link"
            self.properties["feeds"] = ["https://page-with-rss-link.com/feed"]
        elif url == "https://page-with-rss-link.com/feed":
            self.set_entries(10)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["title"] = "Page with RSS link - RSS contents"
        elif url == "https://www.codeproject.com/WebServices/NewsRSS.aspx":
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["thumbnail"] = (
                "https://www.codeproject.com/App_Themes/Std/Img/logo100x30.gif"
            )
        elif url == "https://no-props-page.com":
            self.properties["title"] = None
            self.properties["description"] = None
            self.properties["date_published"] = None
            self.properties["author"] = None
            self.properties["language"] = None
            self.properties["album"] = None
            self.properties["page_rating"] = 0
            self.properties["thumbnail"] = None
        elif url == "https://page-with-http-status-615.com":
            self.response["status_code"] = HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS
        elif url == "https://page-with-http-status-614.com":
            self.response["status_code"] = HTTP_STATUS_CODE_SERVER_ERROR
        elif url == "https://page-with-http-status-600.com":
            self.response["status_code"] = HTTP_STATUS_CODE_EXCEPTION
        elif url == "https://page-with-http-status-500.com":
            self.response["status_code"] = 500
        elif url == "https://page-with-http-status-429.com":
            self.response["status_code"] = HTTP_STATUS_TOO_MANY_REQUESTS
        elif url == "https://page-with-http-status-403.com":
            self.response["status_code"] = HTTP_STATUS_USER_AGENT
        elif url == "https://page-with-http-status-400.com":
            self.response["status_code"] = 400
        elif url == "https://page-with-http-status-300.com":
            self.response["status_code"] = 300
        elif url == "https://page-with-http-status-200.com":
            self.response["status_code"] = 200
        elif url == "https://page-with-http-status-100.com":
            self.response["status_code"] = 100
        elif url == "http://page-with-http-status-500.com":
            self.response["status_code"] = 500
        elif url == "http://page-with-http-status-400.com":
            self.response["status_code"] = 400
        elif url == "http://page-with-http-status-300.com":
            self.response["status_code"] = 300
        elif url == "http://page-with-http-status-200.com":
            self.response["status_code"] = 200
        elif url == "http://page-with-http-status-100.com":
            self.response["status_code"] = 100
        elif url == "https://www.youtube.com/watch?v=666":
            self.response["status_code"] = 500
        elif url == "https://invalid.rsspage.com/rss.xml":
            self.response["status_code"] = 500
        elif (
            url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        ):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [url]
        elif (
            url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=NOLANGUAGETIMESAMTIMESAM"
        ):
            self.set_entries(13, language=None)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [url]
            self.properties["language"] = None
        elif url.startswith("https://odysee.com/$/rss"):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [url]
        elif url == "https://www.geekwire.com/feed":
            self.text_data = geekwire_feed
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [url]
        elif (
            url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id"
        ):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [url]
        elif url == "https://instance.com/apps/rsshistory/sources-json":
            self.properties["title"] = "Instance Proxy"
        elif url == "https://v.firebog.net/hosts/AdguardDNS.txt":
            self.text_data = firebog_adguard_list
        elif url == "https://v.firebog.net/hosts/static/w3kbl.txt":
            self.text_data = firebog_w3kbl_list
        elif url == "https://v.firebog.net/hosts/lists.php?type=tick":
            self.text_data = firebog_tick_lists
        elif url == "https://v.firebog.net/hosts/RPiList-Malware.txt":
            self.text_data = firebog_malware
        elif url == "https://casino.com":
            self.properties["title"] = "Casino Casino Casino"
            self.properties["description"] = "Casino Casino Casino"
        elif url == "https://nfsw.com":
            self.properties["title"] = "AI NSFW girlfriend"
            self.properties["description"] = "AI NSFW girlfriend"
        elif url == "https://binary.com/file":
            self.properties["title"] = ""
            self.properties["description"] = ""
            self.binary_data = "text".encode()

        if url.find("reddit") >= 0:
            self.properties["language"] = "en"

        if self.response["status_code"] > 200 and self.response["status_code"] < 400:
            self.response["is_valid"] = True
            self.response["is_invalid"] = False
        elif self.response["status_code"] < 200:
            self.response["is_valid"] = False
            self.response["is_invalid"] = True
        elif self.response["status_code"] == HTTP_STATUS_USER_AGENT:
            self.response["is_valid"] = False
            self.response["is_invalid"] = False
        elif self.response["status_code"] == HTTP_STATUS_TOO_MANY_REQUESTS:
            self.response["is_valid"] = False
            self.response["is_invalid"] = False
        elif self.response["status_code"] == HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS:
            self.response["is_valid"] = False
            self.response["is_invalid"] = False
        elif self.response["status_code"] == HTTP_STATUS_CODE_SERVER_ERROR:
            self.response["is_valid"] = False
            self.response["is_invalid"] = False
        elif self.response["status_code"] >= 400:
            self.response["is_valid"] = False
            self.response["is_invalid"] = True

        return self.get_all_properties()

    def set_entries(self, number=1, language="en"):
        for item in range(0, number):
            properties = {}
            properties["link"] = self.url + str(item)
            properties["title"] = "Title" + str(item)
            properties["description"] = "Description" + str(item)
            properties["date_published"] = DateUtils.get_datetime_now_iso()
            properties["author"] = "Description"
            properties["language"] = language
            properties["album"] = "Description"
            properties["page_rating"] = 80
            properties["thumbnail"] = None

            self.entries.append(properties)

    def get_socialj(self, url):
        if url.find("youtube.com") >= 0:
            return {"view_count": 15, "thumbs_up": 1, "thumbs_down": 0}
        if url.find("github.com") >= 0:
            return {"stars": 5}
        if url.find("news.ycombinator.com") >= 0:
            return {"upvote_diff": 5}
        if url.find("reddit.com") >= 0:
            return {"upvote_ratio": 5}

        return None

    def get_feedsj(self, url, settings=None):
        return []

    def get_pingj(self, url, settings=None):
        return True


class FlaskArgs(object):
    def __init__(self):
        self._map = {}

    def get(self, key):
        if key in self._map:
            return self._map[key]

    def set(self, key, value):
        self._map[key] = value

    def __contains__(self, key):
        return key in self._map

    def __getitem__(self, key):
        return self._map[key]


class FlaskRequest(object):
    """
    Used to mock flask requests
    """

    def __init__(self, host):
        self.host = host
        self.args = FlaskArgs()

    def set(self, key, value):
        self.args.set(key, value)
