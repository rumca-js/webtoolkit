"""
Provides interface and page types Html, RSS, JSON etc.
"""

from bs4 import BeautifulSoup
import json
from dateutil import parser
from brutefeedparser import BruteFeedParser
import html
import lxml.etree as ET

from .utils.dateutils import DateUtils

from .webtools import (
    calculate_hash,
    WebLogger,
    date_str_to_date,
)
from .urllocation import UrlLocation
from .contentinterface import ContentInterface
from .contentlinkparser import ContentLinkParser


class DefaultContentPage(ContentInterface):
    def __init__(self, url, contents=""):
        super().__init__(url=url, contents=contents)

    def get_title(self):
        return None

    def get_description(self):
        return None

    def get_language(self):
        return None

    def get_thumbnail(self):
        return None

    def get_author(self):
        return None

    def get_album(self):
        return None

    def get_tags(self):
        return None

    def get_date_published(self):
        """
        This should be date. Not string
        """
        return None

    def is_valid(self):
        return True

    def get_response(self):
        return ""


class JsonPage(ContentInterface):
    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

        self.json_obj = None
        try:
            contents = self.get_contents()
            self.json_obj = json.loads(contents)
            if self.json_obj != {}:
                self.json_obj = None
        except ValueError:
            # to be expected
            try:
                WebLogger.debug(f"Invalid json:{contents}")
            except Exception as E:
                print(str(E))

    def is_valid(self):
        if self.json_obj:
            return True

    def get_title(self):
        if self.json_obj and "title" in self.json_obj:
            return str(self.json_obj["title"])

    def get_description(self):
        if self.json_obj and "description" in self.json_obj:
            return str(self.json_obj["description"])

    def get_language(self):
        if self.json_obj and "language" in self.json_obj:
            return str(self.json_obj["language"])

    def get_thumbnail(self):
        if self.json_obj and "thumbnail" in self.json_obj:
            return str(self.json_obj["thumbnail"])

    def get_author(self):
        if self.json_obj and "author" in self.json_obj:
            return str(self.json_obj["author"])

    def get_album(self):
        if self.json_obj and "album" in self.json_obj:
            return str(self.json_obj["album"])

    def get_tags(self):
        if self.json_obj and "tags" in self.json_obj:
            return str(self.json_obj["tags"])

    def get_date_published(self):
        if self.json_obj and "date_published" in self.json_obj:
            return date_str_to_date(self.json_obj["date_published"])

    def get_page_rating(self):
        return 0


class RssPageEntry(ContentInterface):
    def __init__(self, feed_index, feed_entry, url, contents, page_object_properties):
        """ """
        self.feed_index = feed_index
        self.feed_entry = feed_entry
        self.url = url
        self.contents = contents
        self.page_object_properties = page_object_properties

        super().__init__(url=self.url, contents=contents)

    def get_properties(self):
        """ """
        output_map = {}

        link = None

        if "link" in self.feed_entry:
            if self.feed_entry.link != "":
                link = self.feed_entry.link
            else:
                link = self.try_to_extract_link()

        if not link:
            return output_map

        link = link.strip()

        output_map = super().get_properties()

        output_map["link"] = link
        output_map["source"] = self.url
        output_map["bookmarked"] = False
        output_map["feed_entry"] = self.feed_entry

        return output_map

    def try_to_extract_link(self):
        """
        For:
         - https://thehill.com/feed
         - https://warhammer-community.com/feed

        feedparser provide empty links
        Trying to work around that issue.

        RSS can have <entry, or <item things inside

        TODO this should be parsed using beautiful soup
        """
        contents = self.contents

        item_search_wh = contents.find("<item", 0)
        entry_search_wh = contents.find("<entry", 0)

        index = 0
        wh = 0
        while index <= self.feed_index:
            if item_search_wh >= 0:
                wh = contents.find("<item", wh + 1)
                if wh == -1:
                    return
            if entry_search_wh >= 0:
                wh = contents.find("<entry", wh + 1)
                if wh == -1:
                    return

            index += 1

        wh = contents.find("<link", wh + 1)
        if wh == -1:
            return

        wh = contents.find(">", wh + 1)
        if wh == -1:
            return

        wh2 = contents.find("<", wh + 1)
        if wh2 == -1:
            return

        text = contents[wh + 1 : wh2]

        return text

    def get_title(self):
        return self.feed_entry.title

    def get_description(self):
        if hasattr(self.feed_entry, "description"):
            return self.feed_entry.description
        else:
            return ""

    def get_thumbnail(self):
        if hasattr(self.feed_entry, "media_thumbnail"):
            if len(self.feed_entry.media_thumbnail) > 0:
                thumb = self.feed_entry.media_thumbnail[0]
                if "url" in thumb:
                    return thumb["url"]
                else:
                    return str(thumb)
        if hasattr(self.feed_entry, "media_content"):
            if len(self.feed_entry.media_content) > 0:
                thumb = self.feed_entry.media_content[0]
                if "url" in thumb:
                    return thumb["url"]
                else:
                    return str(thumb)
        if hasattr(self.feed_entry, "images"):
            if len(self.feed_entry.images) > 0:
                thumb = self.feed_entry.images[0]
                if "url" in thumb:
                    return thumb["url"]
                else:
                    return str(thumb)

        return None

    def get_language(self):
        if "language" in self.page_object_properties:
            return self.page_object_properties["language"]

    def get_date_published(self):
        date = self.get_date_published_implementation()

        now = DateUtils.get_datetime_now_utc()

        if not date:
            date = now
        if date > now:
            date = now

        return date

    def get_date_published_implementation(self):
        if hasattr(self.feed_entry, "published"):
            if not self.feed_entry.published or str(self.feed_entry.published) == "":
                return DateUtils.get_datetime_now_utc()
            else:
                try:
                    dt = parser.parse(self.feed_entry.published)
                    # TODO this might not be precise, but we do not have to be precise?

                    utc = DateUtils.to_utc_date(dt)
                    return utc

                except Exception as E:
                    WebLogger.error(
                        "RSS parser {} datetime invalid feed datetime:{};\nFeed DateTime:{};\nExc:{}\n".format(
                            self.url,
                            self.feed_entry.published,
                            self.feed_entry.published,
                            str(E),
                        )
                    )
                return DateUtils.get_datetime_now_utc()

    def get_author(self):
        author = None
        if not author and hasattr(self.feed_entry, "author"):
            author = self.feed_entry.author

        if not author and "author" in self.page_object_properties:
            author = self.page_object_properties["author"]

        return author

    def get_album(self):
        return ""

    def get_tags(self):
        if "tags" in self.feed_entry:
            return self.feed_entry.tags

        return None


class RssPage(ContentInterface):
    """
    Handles RSS parsing.
    Do not use feedparser directly enywhere. We use BasicPage
    which allows to define timeouts.
    """

    def __init__(self, url, contents):
        self.feed = None

        """
        Workaround for https://warhammer-community.com/feed
        """
        super().__init__(url=url, contents=contents)

        if self.contents and not self.feed:
            self.process_contents()

    def process_contents(self):
        self.try_to_parse()

        if not self.feed or not self.feed.entries:
            if self.contents.find("html") >= 0 and self.contents.find("rss") >= 0:
                self.try_to_workaround()
        #    WebLogger.error("Feed does not have any entries {}".format(self.url))

        return self.feed

    def try_to_parse(self):
        contents = self.contents
        if contents is None:
            return None

        try:
            self.feed = BruteFeedParser.parse(contents)
            return self.feed
        except Exception as E:
            print(str(E))
            WebLogger.exc(E, "Url:{}. RssPage, when parsing.".format(self.url))

    def try_to_workaround(self):
        if not self.contents:
            return

        start_index = self.contents.find("&lt;rss")
        end_index = self.contents.rfind("&gt;")
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            return

        self.contents = self.contents[start_index : end_index + 4]
        self.contents = html.unescape(self.contents)

        self.try_to_parse()

    def get_entries(self):
        if self.feed is None:
            return

        try:
            for item in self.get_container_elements_maps():
                yield item

        except Exception as E:
            WebLogger.exc(E, "Url:{}. RSS parsing error".format(self.url))

    def get_container_elements_maps(self):
        parent_properties = {}
        parent_properties["language"] = self.get_language()
        parent_properties["author"] = self.get_author()

        contents = self.get_contents()

        for feed_index, feed_entry in enumerate(self.feed.entries):
            rss_entry = RssPageEntry(
                feed_index,
                feed_entry,
                self.url,
                contents,
                parent_properties,
            )
            entry_props = rss_entry.get_properties()

            if not entry_props:
                WebLogger.debug(
                    "No properties for feed entry:{}".format(str(feed_entry))
                )
                continue

            if "link" not in entry_props or entry_props["link"] is None:
                WebLogger.error(
                    "Url:{}. Missing link in RSS".format(self.url),
                    detail_text=str(feed_entry),
                )
                continue

            yield entry_props

    def get_contents_body_hash(self):
        if not self.contents:
            return

        #    WebLogger.error("No rss hash contents")
        #    return calculate_hash("no body hash")
        if not self.feed:
            WebLogger.error(
                "Url:{}. RssPage has contents, but feed could not been analyzed".format(
                    self.url
                )
            )
            return

        entries = str(self.feed.entries)
        if entries == "":
            if self.contents:
                return calculate_hash(self.contents)
        if entries:
            return calculate_hash(entries)

    def get_title(self):
        if self.feed is None:
            return

        if "title" in self.feed.feed:
            return self.feed.feed.title

    def get_description(self):
        if self.feed is None:
            return

        if "description" in self.feed.feed:
            return self.feed.feed.description

        if "subtitle" in self.feed.feed:
            return self.feed.feed.subtitle

    def get_link(self):
        if "link" in self.feed.feed:
            return self.feed.feed.link

    def get_language(self):
        if self.feed is None:
            return

        if "language" in self.feed.feed:
            return self.feed.feed.language

    def get_thumbnail(self):
        if self.feed is None:
            return

        image = None
        if "image" in self.feed.feed:
            if self.feed.feed.image == {}:
                return

            if "href" in self.feed.feed.image:
                try:
                    image = self.feed.feed.image["href"]
                    if image:
                        return str(image)
                except Exception as E:
                    WebLogger.debug(str(E))

            if "url" in self.feed.feed.image:
                try:
                    image = self.feed.feed.image["url"]
                    if image:
                        return str(image)
                except Exception as E:
                    WebLogger.debug(str(E))

            elif "links" in self.feed.feed.image:
                links = self.feed.feed.image["links"]
                if len(links) > 0:
                    WebLogger.error(
                        "I do not know how to process links {}".format(str(links))
                    )
            else:
                WebLogger.error(
                    '<a href="{}">{}</a> Unsupported image type for feed. Image:{}'.format(
                        self.url, self.url, str(self.feed.feed.image)
                    )
                )

        # TODO that does not work
        # if not image:
        #    if self.url.find("https://www.youtube.com/feeds/videos.xml") >= 0:
        #        image = self.get_thumbnail_manual_from_youtube()

        if image and image.lower().find("https://") == -1:
            image = UrlLocation.get_url_full(self.url, image)

        return image

    def get_author(self):
        if self.feed is None:
            return

        if "author" in self.feed.feed:
            return self.feed.feed.author

    def get_album(self):
        if self.feed is None:
            return

        return None

    def get_date_published(self):
        if self.feed is None:
            return

        if "published" in self.feed.feed:
            return date_str_to_date(self.feed.feed.published)

    def get_tags(self):
        if self.feed is None:
            return

        if "tags" in self.feed.feed:
            return self.feed.feed.tags

        return None

    def get_properties(self):
        props = super().get_properties()
        props["contents"] = self.get_contents()
        return props

    def is_valid(self):
        if self.feed and len(self.feed.entries) > 0:
            return True

        if self.get_contents().find("<feed") >= 0:
            return True
        if self.get_contents().find("<rss") >= 0:
            return True

        # if not self.is_contents_rss():
        #     return False

        return False

    def is_contents_rss(self):
        """
        We want the checks to be simple yet effective. Check some tokens.

        There can be RSS sources in HTML, HTML inside RSS. Beware
        """
        if not self.contents:
            return

        # html_tags = self.get_position_of_html_tags()
        rss_tags = self.get_position_of_rss_tags()

        # if html_tags >= 0 and rss_tags >= 0:
        #    return rss_tags < html_tags
        if rss_tags >= 0:
            return True

    def get_charset(self):
        """
        TODO read from encoding property of xml
        """
        if not self.contents:
            return None

        if self.contents.find("encoding") >= 0:
            return "utf-8"

    def get_feeds(self):
        return [self.url]


class RssContentReader(object):
    def __init__(self, url, contents):
        self.contents = contents
        self.process()

    def process(self):
        wh_html = self.contents.find("html")
        wh_lt = self.contents.find("&lt;")

        if wh_html == -1:
            return
        if wh_lt == -1:
            return

        if wh_html > wh_lt:
            return

        wh_gt = self.contents.rfind("&gt;")
        if wh_gt == -1:
            return

        self.contents = self.contents[wh_lt : wh_gt + len("&gt;")]
        self.contents = html.unescape(self.contents)


class OpmlPageEntry(ContentInterface):
    def __init__(self, url, contents, opml_entry):
        super().__init__(url=url, contents=contents)
        self.opml_entry = opml_entry
        self.title = None
        self.link = None

        self.parse()

    def parse(self):
        if "xmlUrl" in self.opml_entry.attrib:
            self.url = self.opml_entry.attrib["xmlUrl"]
        else:
            self.url = None
        if "title" in self.opml_entry.attrib:
            self.title = self.opml_entry.attrib["title"]

    def get_title(self):
        return self.title

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


class OpmlPage(ContentInterface):
    def __init__(self, url, contents):
        """
        We could provide support for more items
        https://github.com/microsoft/rss-reader-wp/blob/master/RSSReader_WP7/sample-opml.xml
        """
        super().__init__(url=url, contents=contents)
        self.entries = []
        self.parse()

    def parse(self):
        return self.parse_implementation()

    def parse_implementation(self):
        if not self.contents:
            return

        try:
            parser = ET.XMLParser(strip_cdata=False, recover=True)
            self.root = ET.fromstring(self.contents.encode(), parser=parser)
        except Exception as E:
            print(str(E))
            self.root = None

        if self.root is None:
            return

        entries = self.root.findall(".//outline")
        if len(entries) > 0:
            for entry in entries:
                opml_entry = OpmlPageEntry(self.url, self.contents, entry)
                if opml_entry.get_url():
                    self.entries.append(opml_entry)
            return entries

    def get_entries(self):
        return self.entries

    def get_feeds(self):
        result = []
        for entry in self.entries:
            result.append(entry.get_url())

        return result

    def is_valid(self):
        if self.get_contents().find("<opml") >= 0:
            return True


class HtmlPage(ContentInterface):
    """
    Since links can be passed in various ways and formats, all links need to be "normalized" before
    returning.

    formats:
    href="images/facebook.png"
    href="/images/facebook.png"
    href="//images/facebook.png"
    href="https://images/facebook.png"
    """

    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

        if self.contents:
            try:
                self.soup = BeautifulSoup(self.contents, "html.parser")
            except Exception as E:
                WebLogger.exc(E, "Contents type:{}".format(type(self.contents)))
                self.contents = None
                self.soup = None
        else:
            self.soup = None

    def get_head_field(self, field):
        if not self.contents:
            return None

        found_element = self.soup.find(field)
        if found_element:
            value = found_element.string
            if value != "":
                return value

    def get_meta_custom_field(self, field_type, field):
        if not self.contents:
            return None

        find_element = self.soup.find("meta", attrs={field_type: field})
        if find_element and find_element.has_attr("content"):
            return find_element["content"]

    def get_schema_field(self, itemprop):
        elements_with_itemprop = self.soup.find_all(attrs={"itemprop": True})
        for element in elements_with_itemprop:
            itemprop_v = element.get("itemprop")
            if itemprop_v != itemprop:
                continue

            if element.name == "link":
                value = element.get("href")
            elif element.name == "meta":
                value = element.get("content")
            else:
                value = element.text.strip() if element.text else None

            return value

    def get_schema_field_ex(self, itemtype, itemprop):
        """
        itemtype can be "http://schema.org/VideoObject"
        """
        # Find elements with itemtype="http://schema.org/VideoObject"
        video_objects = self.soup.find_all(attrs={"itemtype": itemtype})
        for video_object in video_objects:
            # Extract itemprop from elements inside video_object
            elements_with_itemprop = video_object.find_all(attrs={"itemprop": True})
            for element in elements_with_itemprop:
                itemprop_v = element.get("itemprop")

                if itemprop_v != itemprop:
                    continue

                if element.name == "link":
                    value = element.get("href")
                elif element.name == "meta":
                    value = element.get("content")
                else:
                    value = element.text.strip() if element.text else None

                return value

    def get_meta_field(self, field):
        if not self.contents:
            return None

        return self.get_meta_custom_field("name", field)

    def get_property_field(self, name):
        if not self.contents:
            return None

        field_find = self.soup.find("meta", property="{}".format(name))
        if field_find and field_find.has_attr("content"):
            return field_find["content"]

    def get_og_field(self, name):
        """
        Open Graph protocol: https://ogp.me/
        """
        if not self.contents:
            return None

        return self.get_property_field("og:{}".format(name))

    def get_title(self):
        if not self.contents:
            return None

        title = self.get_og_field("title")

        if not title:
            self.get_schema_field("name")

        if not title:
            title = self.get_title_meta()

        if not title:
            title = self.get_title_head()

        if not title:
            title = self.get_og_site_name()

        if title:
            title = title.strip()

            # TODO hardcoded. Some pages provide such a dumb title with redirect
            if title.find("Just a moment") >= 0:
                title = ""

        return title
        # title = html.unescape(title)

    def get_date_published(self):
        """
        There could be multiple places to read published time.
        We try every possible thing.
        """
        # used by mainstream media. Examples?
        date_str = self.get_property_field("article:published_time")
        if date_str:
            return date_str_to_date(date_str)

        # used by spotify
        date_str = self.get_meta_field("music:release_date")
        if date_str:
            return date_str_to_date(date_str)

        # used by youtube
        date_str = self.get_schema_field("datePublished")
        if date_str:
            return date_str_to_date(date_str)

    def get_title_head(self):
        if not self.contents:
            return None

        return self.get_head_field("title")

    def get_title_meta(self):
        if not self.contents:
            return None

        return self.get_meta_field("title")

    def get_description(self):
        if not self.contents:
            return None

        description = self.get_og_field("description")

        if not description:
            description = self.get_schema_field("description")

        if not description:
            description = self.get_description_meta()

        if not description:
            description = self.get_description_head()

        if description:
            description = description.strip()

        return description

    def get_description_safe(self):
        desc = self.get_description()
        if not desc:
            return ""
        return desc

    def get_description_head(self):
        if not self.contents:
            return None

        return self.get_head_field("description")

    def get_description_meta(self):
        if not self.contents:
            return None

        return self.get_meta_field("description")

    def get_thumbnail(self):
        if not self.contents:
            return None

        image = self.get_og_field("image")

        if not image:
            image = self.get_schema_field("thumbnailUrl")

        if not image:
            image = self.get_schema_field("image")

        # do not return favicon here.
        # we use thumbnails in <img, but icons do not work correctly there

        if image and image.lower().find("https://") == -1:
            image = UrlLocation.get_url_full(self.url, image)

        return image

    def get_language(self):
        if not self.contents:
            return ""

        html = self.soup.find("html")
        if html and html.has_attr("lang"):
            return html["lang"]

        locale = self.get_og_locale()
        if locale:
            return locale

        return ""

    def get_charset(self):
        if not self.contents:
            return None

        charset = None

        allmeta = self.soup.findAll("meta")
        for meta in allmeta:
            for attr in meta.attrs:
                if attr.lower() == "charset":
                    return meta.attrs[attr]
                if attr.lower() == "http-equiv":
                    if "content" in meta.attrs:
                        text = meta.attrs["content"].lower()
                        wh = text.find("charset")
                        if wh >= 0:
                            wh2 = text.find("=", wh)
                            if wh2 >= 0:
                                charset = text[wh2 + 1 :].strip()
                                return charset

    def get_author(self):
        """
        <head><author>Something</author></head>
        """
        if not self.contents:
            return None

        author = self.get_meta_field("author")
        if not author:
            author = self.get_og_field("author")

        return author

    def get_album(self):
        return None

    def get_favicons(self, recursive=False):
        if not self.contents:
            return {}

        favicons = {}

        link_finds = self.soup.find_all("link", attrs={"rel": "icon"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                full_favicon = link_find["href"]
                if full_favicon.strip() == "":
                    continue
                full_favicon = UrlLocation.get_url_full(self.url, full_favicon)
                if "sizes" in link_find:
                    favicons[full_favicon] = link_find["sizes"]
                else:
                    favicons[full_favicon] = ""

        link_finds = self.soup.find_all("link", attrs={"rel": "shortcut icon"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                full_favicon = link_find["href"]
                if full_favicon.strip() == "":
                    continue
                full_favicon = UrlLocation.get_url_full(self.url, full_favicon)
                if "sizes" in link_find:
                    favicons[full_favicon] = link_find["sizes"]
                else:
                    favicons[full_favicon] = ""

        return favicons

    def get_favicon(self):
        favicons = self.get_favicons()
        for favicon in favicons:
            return favicon

    def get_tags(self):
        if not self.contents:
            return None

        return self.get_meta_field("keywords")

    def get_canonical_url(self):
        canonical_tag = self.soup.find("link", rel="canonical")
        if canonical_tag:
            canonical_link = canonical_tag.get("href")
            if canonical_link and canonical_link.endswith("/"):
                return canonical_link[:-1]
            return canonical_link

    def get_og_title(self):
        return self.get_og_field("title")

    def get_og_description(self):
        return self.get_og_field("description")

    def get_og_site_name(self):
        return self.get_og_field("site_name")

    def get_og_image(self):
        return self.get_og_field("image")

    def get_og_locale(self):
        return self.get_og_field("locale")

    def get_rss_url(self, full_check=False):
        urls = self.get_feeds()
        if urls and len(urls) > 0:
            return urls[0]

    def get_feeds(self):
        if not self.contents:
            return []

        rss_links = self.find_feed_links("application/rss+xml") + self.find_feed_links(
            "application/atom+xml"
        )

        # if not rss_links:
        #    links = self.get_links_inner()
        #    rss_links.extend(
        #        link
        #        for link in links
        #        if "feed" in link or "rss" in link or "atom" in link
        #    )

        return (
            [UrlLocation.get_url_full(self.url, rss_url) for rss_url in rss_links]
            if rss_links
            else []
        )

    def find_feed_links(self, feed_type):
        result_links = []

        found_elements = self.soup.find_all("link")
        for found_element in found_elements:
            if found_element.has_attr("type"):
                link_type = str(found_element["type"])
                if link_type.find(feed_type) >= 0:
                    if found_element.has_attr("href"):
                        result_links.append(found_element["href"])
                    else:
                        WebLogger.error(
                            "Found {} link without href. Str:{}".format(
                                feed_type, str(found_element)
                            )
                        )

        return result_links

    def get_links(self):
        p = ContentLinkParser(self.url, self.contents)
        links = p.get_links()
        links = ContentLinkParser.filter_link_html(links)
        return links

    def get_links_inner(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_links_inner()

    def get_links_outer(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_links_outer()

    def get_domains(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_domains()

    def get_domain_page(self):
        if self.url == self.get_domain():
            return self

        return Page(self.get_domain())

    def get_properties(self):
        props = super().get_properties()

        props["meta_title"] = self.get_title_meta()
        props["meta_description"] = self.get_description_meta()
        props["og_title"] = self.get_og_title()
        props["og_description"] = self.get_og_description()
        props["og_site_name"] = self.get_og_site_name()
        props["og_locale"] = self.get_og_locale()
        props["og_image"] = self.get_og_image()
        # props["is_html"] = self.is_html()
        props["charset"] = self.get_charset()
        props["feeds"] = self.get_feeds()
        # props["status_code"] = self.status_code

        # if UrlLocation(self.url).is_domain():
        #    if self.is_robots_txt():
        #        props["robots_txt_url"] = UrlLocation(self.url).get_robots_txt_url()
        #        props["site_maps_urls"] = self.get_site_maps()

        #props["links"] = self.get_links()
        #props["links_inner"] = self.get_links_inner()
        #props["links_outer"] = self.get_links_outer()

        props["favicons"] = self.get_favicons()
        props["contents"] = self.get_contents()
        if self.get_contents():
            props["contents_length"] = len(self.get_contents())

        return props

    def get_page_rating_vector(self):
        rating = []

        title_meta = self.get_title_meta()
        title_og = self.get_og_title()
        description_meta = self.get_description_meta()
        description_og = self.get_og_description()
        image_og = self.get_og_image()
        language = self.get_language()

        rating.append(self.get_page_rating_title(title_meta))
        rating.append(self.get_page_rating_title(title_og))
        rating.append(self.get_page_rating_description(description_meta))
        rating.append(self.get_page_rating_description(description_og))
        rating.append(self.get_page_rating_language(language))
        # rating.append(self.get_page_rating_status_code(self.response.status_code))

        if self.get_author() != None:
            rating.append([1, 1])
        if self.get_tags() != None:
            rating.append([1, 1])

        if self.get_date_published() != None:
            rating.append([3, 3])

        if image_og:
            rating.append([5, 5])

        return rating

    def get_page_rating_title(self, title):
        rating = 0
        if title is not None:
            if len(title) > 1000:
                rating += 5
            elif len(title.split(" ")) < 2:
                rating += 5
            elif len(title) < 4:
                rating += 2
            else:
                rating += 10

        return [rating, 10]

    def get_page_rating_description(self, description):
        rating = 0
        if description is not None:
            rating += 5

        return [rating, 5]

    def get_page_rating_language(self, language):
        rating = 0
        if language is not None:
            rating += 5
        if language.find("en") >= 0:
            rating += 1

        return [rating, 5]

    def is_valid(self):
        """
        This is a simple set of rules in which we reject the page:
         - status code
         - if valid HTML code
        """
        if not self.is_contents_html():
            return False

        return True

    def is_contents_html(self):
        """
        We want the checks to be simple yet effective. Check some tokens.

        There can be RSS sources in HTML, HTML inside RSS. Beware
        """
        if not self.contents:
            WebLogger.debug("Could not obtain contents for {}".format(self.url))
            return

        html_tags = self.get_position_of_html_tags()
        rss_tags = self.get_position_of_rss_tags()

        if html_tags >= 0 and rss_tags >= 0:
            return html_tags < rss_tags
        if html_tags >= 0:
            return True

    def get_body_text(self):
        if not self.contents:
            return

        body_find = self.soup.find("body")
        if not body_find:
            return

        return body_find.get_text()

    def get_contents_body_hash(self):
        if not self.contents:
            return

        body = self.get_body_text()

        if body == "":
            return calculate_hash(body)
        elif body:
            return calculate_hash(body)
        else:
            WebLogger.error("HTML: Cannot calculate body hash for:{}".format(self.url))
            if self.contents:
                return calculate_hash(self.contents)

    def is_pwa(self):
        """
        @returns true, if it is progressive web app
        """
        if self.get_pwa_manifest():
            return True

    def get_pwa_manifest(self):
        link_finds = self.soup.find_all("link", attrs={"rel": "manifest"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                manifest_path = link_find["href"]

                return manifest_path


class XmlPage(ContentInterface):
    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

    def is_valid(self):
        """
        This is a simple set of rules in which we reject the page:
         - status code
         - if valid HTML code
        """
        if not self.is_contents_xml():
            return False

        return True

    def is_contents_xml(self):
        if not self.get_contents():
            return False

        contents = self.get_contents()

        lower = contents.lower()
        if lower.find("<?xml") >= 0:
            return lower.find("<?xml") >= 0


class PageFactory(object):
    def get(response, contents):
        """
        Note: some servers might return text/html for RSS sources.
              We must manually check what kind of data it is.
              For speed - we check first what is suggested by content-type
        """
        contents = None
        if response and response.get_text():
            contents = response.get_text()

        if not contents:
            return

        url = response.request_url

        if response.is_html():
            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = OpmlPage(url, contents)
            if p.is_valid():
                return p

            p = JsonPage(url, contents)
            if p.is_valid():
                return p

        if response.is_rss():
            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = OpmlPage(url, contents)
            if p.is_valid():
                return p

            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

            p = JsonPage(url, contents)
            if p.is_valid():
                return p

        if response.is_json():
            p = JsonPage(url, contents)
            if p.is_valid():
                return p

            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

        if response.is_content_type("image"):
            return
        if response.is_content_type("audio"):
            return
        if response.is_content_type("video"):
            return
        if response.is_content_type("font"):
            return

        # we do not know what it is. Guess

        p = HtmlPage(url, contents)
        if p.is_valid():
            return p

        p = RssPage(url, contents)
        if p.is_valid():
            return p

        p = OpmlPage(url, contents)
        if p.is_valid():
            return p

        p = JsonPage(url, contents)
        if p.is_valid():
            return p

        # TODO
        # p = XmlPage(url, contents)
        # if p.is_valid():
        #    return p

        if response.is_text():
            p = DefaultContentPage(url, contents)
            return p

        p = DefaultContentPage(url, contents)
        return p


class YouTubeVideoJson(object):
    def __init__(self, url=None):
        self._json = {}
        self.url = url

    def get_json_data(self):
        return json.dumps(self._json)

    def is_valid(self):
        return self._json != {}

    def get_json(self):
        return self._json

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            logging.critical(E, exc_info=True)

    def write(self, file_name, force=True):
        file_dir = os.path.split(file_name)[0]

        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        with open(file_name, "w", encoding="utf-8") as fh:
            fh.write(self.get_json_data())

    def read(self, file_name):
        if not os.path.isfile(file_name):
            return None

        with open(file_name, "r", encoding="utf-8") as fh:
            data = fh.read()
            self.loads(data)

    def is_valid(self):
        if "title" in self._json and "t_likes" in self._json:
            return True
        else:
            return False

    def get_file_name(self):
        if len(self._json) > 0:
            return self._json["_filename"]

    def get_duration(self):
        if len(self._json) > 0:
            return self._json["duration"]

    def get_link(self):
        if len(self._json) > 0:
            return self._json["url"]

    def get_title(self):
        if len(self._json) > 0:
            return self._json["title"]

    def get_thumbnail(self):
        if len(self._json) > 0:
            if "thumbnail" in self._json:
                return self._json["thumbnail"]
            else:
                if "thumbnails" in self._json:
                    return self._json["thumbnails"][0]["url"]

    def get_stretched_ratio(self):
        if len(self._json) > 0:
            return self._json["stretched_ratio"]

    def get_tags(self):
        if len(self._json) > 0:
            if "tags" in self._json:
                return self._json["tags"]

    def get_categories(self):
        if len(self._json) > 0:
            return self._json["categories"]

    def get_date_published(self):
        if len(self._json) > 0:
            if "upload_date" in self._json:
                return self._json["upload_date"]
            if "epoch" in self._json:
                epoch = self._json["epoch"]
                if epoch:
                    date_utc = datetime.utcfromtimestamp(epoch)
                    if date_utc:
                        return date_utc
            if "timestamp" in self._json:
                return self._json["timestamp"]

    def get_description(self):
        if len(self._json) > 0:
            return self._json["description"]

    def get_video_length(self):
        if len(self._json) > 0:
            return int(self._json["duration"])

    def get_chapters(self):
        # chapter => end_time, start_time, title
        if len(self._json) > 0:
            if "chapters" in self._json:
                return self._json["chapters"]

    def get_channel_name(self):
        if len(self._json) > 0:
            return self._json["channel"]

    def get_channel_url(self):
        if len(self._json) > 0:
            return self._json["channel_url"]

    def get_channel_code(self):
        if len(self._json) > 0:
            return self._json["channel_id"]

    def get_followers_count(self):
        if len(self._json) > 0:
            return self._json["channel_follower_count"]

    def get_channel_feed_url(self):
        if len(self._json) > 0:
            return "https://www.youtube.com/feeds/videos.xml?channel_id={}".format(
                self.get_channel_code()
            )

    def get_view_count(self):
        if len(self._json) > 0:
            if "view_count" in self._json:
                return str(self._json["view_count"])

            # return self._json["t_view_count"]
        return 0

    def get_thumbs_up(self):
        if len(self._json) > 0:
            if "like_count" in self._json:
                return str(self._json["like_count"])
            else:
                print("No like_count in self._json {}".format(self._json))
            # return self._json["t_likes"]

        return 0

    def get_thumbs_down(self):
        if len(self._json) > 0:
            return self._json["t_dislikes"]

    def get_rating(self):
        if len(self._json) > 0:
            return self._json["t_rating"]

    def get_upload_date(self):
        if len(self._json) > 0:
            return self._json["upload_date"]

    def is_live(self):
        if len(self._json) > 0:
            is_live = False
            if "live_status" in self._json:
                not_alive = (
                    self._json["live_status"] == "not_live"
                    or self._json["live_status"] == "False"
                )

                is_live = not not_alive

            was_live = False
            if "was_live" in self._json:
                was_live = self._json["was_live"]

            return is_live or was_live
        return False

    def get_link_url(self):
        if len(self._json) > 0:
            return "https://www.youtube.com/watch?v={}".format(self._json["id"])

    def add_return_dislike_data(self, rdd):
        self._json["t_likes"] = rdd.get_likes()
        self._json["t_dislikes"] = rdd.get_dislikes()
        self._json["t_view_count"] = rdd.get_view_count()
        self._json["t_rating"] = rdd.get_rating()


class ReturnDislikeJson(object):
    def __init__(self, url=None, contents=None):
        self.contents = contents
        self.load_response()

    def load_response(self):
        self._json = self.loads(self.contents)
        return self._json

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            self._json = {}

    def get_json(self):
        return self._json

    def get_thumbs_up(self):
        if self._json:
            return self._json.get("likes")

    def get_thumbs_down(self):
        if self._json:
            return self._json.get("dislikes")

    def get_view_count(self):
        if self._json:
            return self._json.get("viewCount")

    def get_rating(self):
        if self._json:
            return self._json.get("rating")

    def get_json_data(self):
        self.get_response()
