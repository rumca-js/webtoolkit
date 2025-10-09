"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

import logging
import unittest
import traceback

from utils.dateutils import DateUtils
from webtoolkit import (
    PageResponseObject,
    WebLogger,
    WebConfig,
    ResponseHeaders,
    RemoteServer,
    json_encode_field,
    json_decode_field,
    HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_USER_AGENT,
)

from tests.fakeinternetdata import (
    webpage_with_real_rss_links,
    webpage_simple_rss_page,
    webpage_old_pubdate_rss,
    webpage_no_pubdate_rss,
    webpage_html_favicon,
    webpage_with_rss_link_rss_contents,
    webpage_html_casinos,
    webpage_html_canonical_1,
)
from tests.fake.geekwirecom import (
    geekwire_feed,
)
from tests.fake.youtube import (
    youtube_robots_txt,
    youtube_sitemap_sitemaps,
    youtube_sitemap_product,
    webpage_youtube_airpano_feed,
    webpage_samtime_odysee,
    webpage_samtime_youtube_rss,
    youtube_channel_html_linus_tech_tips,
    youtube_channel_rss_linus_tech_tips,
)
from tests.fake.robotstxtcom import (
    robots_txt_example_com_robots,
)
from tests.fake.codeproject import (
    webpage_code_project_rss,
)
from tests.fake.opmlfile import (
    opml_file,
)
from tests.fake.hackernews import (
    webpage_hackernews_rss,
    hacker_news_item,
)
from tests.fake.warhammercommunity import (
    warhammer_community_rss,
)
from tests.fake.thehill import (
    thehill_rss,
)
from tests.fake.reddit import (
    reddit_rss_text,
    reddit_entry_json,
    reddit_subreddit_json,
)
from tests.fake.githubcom import (
    github_json,
)
from tests.fake.returndislike import (
    return_dislike_json,
)
from tests.fake.firebog import (
    firebog_adguard_list,
    firebog_w3kbl_list,
    firebog_tick_lists,
    firebog_malware,
)
from tests.fake.instance import (
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

        self.response = {
            "status_code": 200,
            "Content-Length": 200,
            "Content-Type": "text/html",
            "body_hash": json_encode_field(b"01001012"),
            "hash": json_encode_field(b"01001012"),
            "is_valid": True,
            "is_invalid": False,
            "is_allowed": True,
        }
        self.text_data = "Something"
        self.binary_data = None
        self.entries = []

    def get_all_properties(self):
        data = []
        data.append({"name": "Properties", "data": self.properties})
        data.append({"name": "Settings", "data": None})
        data.append({"name": "Response", "data": self.response})
        data.append({"name": "Headers", "data": {}})
        data.append({"name": "Entries", "data": self.entries})
        data.append({"name": "Streams", "data": {
            "Text" : self.text_data,
            "Binary" : json_encode_field(self.binary_data)
            }})

        return data

    def get_getj(self, name="", settings=None):
        if self.url == "https://linkedin.com":
            self.properties["title"] = "Https LinkedIn Page title"
            self.properties["description"] = "Https LinkedIn Page description"
        elif self.url == "https://m.youtube.com/watch?v=1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif self.url == "https://www.youtube.com/watch?v=1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif self.url == "https://youtu.be/1234":
            self.properties["link"] = "https://www.youtube.com/watch?v=1234"
            self.properties["feeds"] = [
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id",
            ]
            self.properties["title"] = "YouTube 1234 video"
            self.properties["language"] = None
        elif self.url == "https://www.reddit.com/r/searchengines/":
            self.properties["feeds"] = ["https://www.reddit.com/r/searchengines/.rss"]
        elif self.url == "https://www.reddit.com/r/searchengines":
            self.properties["feeds"] = ["https://www.reddit.com/r/searchengines/.rss"]
        elif self.url == "https://www.reddit.com/r/searchengines/.rss":
            self.set_entries(10)
        elif self.url == "https://page-with-rss-link.com":
            self.properties["title"] = "Page with RSS link"
            self.properties["feeds"] = ["https://page-with-rss-link.com/feed"]
        elif self.url == "https://page-with-rss-link.com/feed":
            self.set_entries(10)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["title"] = "Page with RSS link - RSS contents"
        elif self.url == "https://www.codeproject.com/WebServices/NewsRSS.aspx":
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["thumbnail"] = (
                "https://www.codeproject.com/App_Themes/Std/Img/logo100x30.gif"
            )
        elif self.url == "https://no-props-page.com":
            self.properties["title"] = None
            self.properties["description"] = None
            self.properties["date_published"] = None
            self.properties["author"] = None
            self.properties["language"] = None
            self.properties["album"] = None
            self.properties["page_rating"] = 0
            self.properties["thumbnail"] = None
        elif self.url == "https://page-with-http-status-615.com":
            self.response["status_code"] = HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS
        elif self.url == "https://page-with-http-status-614.com":
            self.response["status_code"] = HTTP_STATUS_CODE_SERVER_ERROR
        elif self.url == "https://page-with-http-status-600.com":
            self.response["status_code"] = HTTP_STATUS_CODE_EXCEPTION
        elif self.url == "https://page-with-http-status-500.com":
            self.response["status_code"] = 500
        elif self.url == "https://page-with-http-status-429.com":
            self.response["status_code"] = HTTP_STATUS_TOO_MANY_REQUESTS
        elif self.url == "https://page-with-http-status-403.com":
            self.response["status_code"] = HTTP_STATUS_USER_AGENT
        elif self.url == "https://page-with-http-status-400.com":
            self.response["status_code"] = 400
        elif self.url == "https://page-with-http-status-300.com":
            self.response["status_code"] = 300
        elif self.url == "https://page-with-http-status-200.com":
            self.response["status_code"] = 200
        elif self.url == "https://page-with-http-status-100.com":
            self.response["status_code"] = 100
        elif self.url == "http://page-with-http-status-500.com":
            self.response["status_code"] = 500
        elif self.url == "http://page-with-http-status-400.com":
            self.response["status_code"] = 400
        elif self.url == "http://page-with-http-status-300.com":
            self.response["status_code"] = 300
        elif self.url == "http://page-with-http-status-200.com":
            self.response["status_code"] = 200
        elif self.url == "http://page-with-http-status-100.com":
            self.response["status_code"] = 100
        elif self.url == "https://www.youtube.com/watch?v=666":
            self.response["status_code"] = 500
        elif self.url == "https://invalid.rsspage.com/rss.xml":
            self.response["status_code"] = 500
        elif (
            self.url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        ):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [self.url]
        elif (
            self.url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=NOLANGUAGETIMESAMTIMESAM"
        ):
            self.set_entries(13, language=None)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [self.url]
            self.properties["language"] = None
        elif self.url.startswith("https://odysee.com/$/rss"):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [self.url]
        elif self.url == "https://www.geekwire.com/feed":
            self.text_data = geekwire_feed
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [self.url]
        elif (
            self.url
            == "https://www.youtube.com/feeds/videos.xml?channel_id=1234-channel-id"
        ):
            self.set_entries(13)
            self.response["Content-Type"] = "application/rss+xml"
            self.properties["feeds"] = [self.url]
        elif self.url == "https://instance.com/apps/rsshistory/sources-json":
            self.properties["title"] = "Instance Proxy"
        elif self.url == "https://v.firebog.net/hosts/AdguardDNS.txt":
            self.text_data = firebog_adguard_list
        elif self.url == "https://v.firebog.net/hosts/static/w3kbl.txt":
            self.text_data = firebog_w3kbl_list
        elif self.url == "https://v.firebog.net/hosts/lists.php?type=tick":
            self.text_data = firebog_tick_lists
        elif self.url == "https://v.firebog.net/hosts/RPiList-Malware.txt":
            self.text_data = firebog_malware
        elif self.url == "https://casino.com":
            self.properties["title"] = "Casino Casino Casino"
            self.properties["description"] = "Casino Casino Casino"
        elif self.url == "https://nfsw.com":
            self.properties["title"] = "AI NSFW girlfriend"
            self.properties["description"] = "AI NSFW girlfriend"
        elif self.url == "https://binary.com/file":
            self.properties["title"] = ""
            self.properties["description"] = ""
            self.binary_data = "text".encode()

        if self.url.find("reddit") >= 0:
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



class FakeInternetTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MockRequestCounter.reset()

    def disable_web_pages(self):
        WebConfig.use_print_logging()
        RemoteServer.get_getj = self.get_getj
        RemoteServer.get_socialj = self.get_socialj
        RemoteServer.get_feedsj = self.get_feedsj
        RemoteServer.get_pingj = self.get_pingj

    def get_getj(self, url, name="", settings=None):
        # print("FakeInternet:get_getj: Url:{}".format(url))
        # return json.loads(remote_server_json)
        MockRequestCounter.requested(url=url, info=settings)

        data = FakeInternetData(url)
        return data.get_getj(name, settings)

    def get_socialj(self, url):
        MockRequestCounter.requested(url=url)

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

    def setup_configuration(self):
        # each suite should start with a default configuration entry
        c = Configuration.get_object()
        c.config_entry = ConfigurationEntry.get()

        c.config_entry.enable_keyword_support = True
        c.config_entry.enable_domain_support = True
        c.config_entry.accept_domain_links = True
        c.config_entry.accept_non_domain_links = True
        c.config_entry.new_entries_merge_data = False
        c.config_entry.new_entries_use_clean_data = False
        c.config_entry.default_source_state = False
        c.config_entry.auto_create_sources = False
        c.config_entry.auto_scan_new_entries = False
        c.config_entry.enable_link_archiving = False
        c.config_entry.enable_source_archiving = False
        c.config_entry.track_user_actions = False
        c.config_entry.track_user_searches = False
        c.config_entry.track_user_navigation = False
        c.config_entry.days_to_move_to_archive = 100
        c.config_entry.days_to_remove_links = 0
        c.config_entry.respect_robots_txt = False
        c.config_entry.whats_new_days = 7
        c.config_entry.keep_domain_links = True
        c.config_entry.entry_update_via_internet = True

        c.config_entry.save()

        c.apply_robots_txt()

    def get_user(
        self, username="test_username", password="testpassword", is_superuser=False
    ):
        """
        TODO test cases should be rewritten to use names as follows:
         - test_superuser
         - test_staff
         - test_authenticated
        """
        users = User.objects.filter(username=username)
        if users.count() > 0:
            self.user = users[0]
            self.user.username = username
            self.user.password = password
            self.user.is_superuser = is_superuser
            self.user.save()
        else:
            self.user = User.objects.create_user(
                username=username, password=password, is_superuser=is_superuser
            )

        return self.user

    def print_errors(self):
        infos = AppLogging.objects.filter(level=int(logging.ERROR))
        for info in infos:
            print("Error: {}".format(info.info_text))

    def no_errors(self):
        infos = AppLogging.objects.filter(level=int(logging.ERROR))
        return infos.count() == 0

    def create_example_data(self):
        self.create_example_sources()
        self.create_example_links()
        self.create_example_domains()
        self.create_example_exports()

    def create_example_sources(self):
        source1 = SourceDataController.objects.create(
            url="https://youtube.com",
            title="YouTube",
            category="No",
            subcategory="No",
            export_to_cms=True,
        )
        source2 = SourceDataController.objects.create(
            url="https://linkedin.com",
            title="LinkedIn",
            category="No",
            subcategory="No",
            export_to_cms=False,
        )
        return [source1, source2]

    def create_example_links(self):
        """
        All entries are outdated
        """
        entry1 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=bookmarked",
            title="The first link",
            source=source_youtube,
            bookmarked=True,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )
        entry2 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=nonbookmarked",
            title="The second link",
            source=source_youtube,
            bookmarked=False,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )
        entry3 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=permanent",
            title="The first link",
            source=source_youtube,
            permanent=True,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )

        return [entry1, entry2, entry3]

    def create_example_domains(self):
        DomainsController.add("https://youtube.com?v=nonbookmarked")

        DomainsController.objects.create(
            protocol="https",
            domain="youtube.com",
            category="testCategory",
            subcategory="testSubcategory",
        )
        DomainCategories.objects.all().delete()
        DomainSubCategories.objects.all().delete()

    def create_example_keywords(self):
        datetime = KeyWords.get_keywords_date_limit() - timedelta(days=1)
        keyword = KeyWords.objects.create(keyword="test")
        keyword.date_published = datetime
        keyword.save()

        return [keyword]

    def create_example_exports(self):
        export1 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_DAILY_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        export2 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_YEAR_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        export3 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_NOTIME_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        return [export1, export2, export3]

    def create_example_permanent_data(self):
        p1 = AppLogging.objects.create(info="info1", level=10, user="test")
        p1.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p1.save()

        p2 = AppLogging.objects.create(info="info2", level=10, user="test")
        p2.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p2.save()

        p3 = AppLogging.objects.create(info="info3", level=10, user="test")
        p3.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p3.save()

        return [p1, p2, p3]
