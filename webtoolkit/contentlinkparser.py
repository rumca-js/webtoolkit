"""
Provides interface and page types Html, RSS, JSON etc.
"""

import re
import html

from .utils.dateutils import DateUtils

from .webtools import (
    WebLogger,
)
from .urllocation import UrlLocation
from .contentinterface import ContentInterface


class ContentLinkParser(ContentInterface):
    """
    TODO filter also html from non html
    """

    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)
        self.url = UrlLocation(url).get_no_arg_link()

    def get_links(self):
        links = set()

        links.update(self.get_links_https("https"))
        links.update(self.get_links_https_encoded("https"))
        links.update(self.get_links_https("http"))
        links.update(self.get_links_https_encoded("http"))
        links.update(self.get_links_href())

        # TODO - maybe this thing below could be made more clean, or refactored
        result = set()
        for item in links:
            wh = item.find('"')
            if wh != -1:
                item = item[:wh]
            wh = item.find("<")
            if wh != -1:
                item = item[:wh]
            wh = item.find(">")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&quot;")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&gt;")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&lt;")
            if wh != -1:
                item = item[:wh]

            result.add(item.strip())

        links = result

        # This is most probably redundant
        if None in links:
            links.remove(None)
        if "" in links:
            links.remove("")
        if "http" in links:
            links.remove("http")
        if "https" in links:
            links.remove("https")
        if "http://" in links:
            links.remove("http://")
        if "https://" in links:
            links.remove("https://")

        result = set()
        for link in links:
            if UrlLocation(link).is_web_link():
                result.add(link)

        return links

    def get_links_https(self, protocol="https"):
        cont = str(self.get_contents())

        pattern = "(" + protocol + "?://[a-zA-Z0-9./\-_?&=#;:]+)"

        all_matches = re.findall(pattern, cont)
        # links cannot end with "."
        all_matches = [link.rstrip(".") for link in all_matches]
        return set(all_matches)

    def get_links_https_encoded(self, protocol="https"):
        cont = str(self.get_contents())

        pattern = "(" + protocol + "?:&#x2F;&#x2F;[a-zA-Z0-9./\-_?&=#;:]+)"

        all_matches = re.findall(pattern, cont)
        # links cannot end with "."
        all_matches = [link.rstrip(".") for link in all_matches]
        all_matches = [ContentLinkParser.decode_url(link) for link in all_matches]

        return all_matches

    def join_url_parts(self, partone, parttwo):
        if not partone.endswith("/"):
            partone = partone + "/"
        if parttwo.startswith("/"):
            parttwo = parttwo[1:]

        return partone + parttwo

    def decode_url(url):
        return html.unescape(url)

    def get_links_href(self):
        links = set()

        url = self.url
        domain = UrlLocation(self.url).get_domain()

        cont = str(self.get_contents())

        all_matches = re.findall('href="([a-zA-Z0-9./\-_?&=@#;:]+)', cont)

        for item in all_matches:
            ready_url = None

            item = item.strip()

            # exclude mailto: tel: sms:
            pattern = "^[a-zA-Z0-9]+:"
            if re.match(pattern, item):
                if (
                    not item.startswith("http")
                    and not item.startswith("ftp")
                    and not item.startswith("smb")
                ):
                    wh = item.find(":")
                    item = item[wh + 1 :]

            if item.startswith("//"):
                if not item.startswith("http"):
                    item = "https:" + item

            if item.startswith("/"):
                item = self.join_url_parts(domain, item)

            # for urls like user@domain.com/location
            pattern = "^[a-zA-Z0-9]+@"
            if re.match(pattern, item):
                wh = item.find("@")
                item = item[wh + 1 :]

            # not absolute path
            if not (item.startswith("http") and not item.startswith("ftp")):
                if item.count(".") <= 0:
                    item = self.join_url_parts(url, item)
                else:
                    if not item.startswith("http"):
                        item = "https://" + item

            if item.startswith("https:&#x2F;&#x2F") or item.startswith(
                "http:&#x2F;&#x2F"
            ):
                item = ContentLinkParser.decode_url(item)

            if item:
                links.add(item)

        return links

    def filter_link_html(links):
        result = set()
        for link in links:
            p = UrlLocation(link)
            if p.is_link():
                result.add(link)

        return result

    def filter_link_in_domain(links, domain):
        result = set()

        for link in links:
            if link.find(domain) >= 0:
                result.add(link)

        return result

    def filter_link_in_url(links, url):
        result = set()

        for link in links:
            if link.find(url) >= 0:
                result.add(link)

        return result

    def filter_link_out_domain(links, domain):
        result = set()

        for link in links:
            if link.find(domain) < 0:
                result.add(link)

        return result

    def filter_link_out_url(links, url):
        result = set()

        for link in links:
            if link.find(url) < 0:
                result.add(link)

        return result

    def filter_domains(links):
        result = set()
        for link in links:
            p = UrlLocation(link)
            new_link = p.get_domain()
            if new_link == "https://" or new_link == "http://":
                WebLogger.debug(
                    "Incorrect link to add: {}".format(new_link), stack=True
                )
                continue

            if not p.is_web_link():
                continue

            if new_link:
                result.add(new_link)

        return result

    def get_domains(self):
        links = self.get_links()
        links = ContentLinkParser.filter_domains(links)

        # TODO This is most probably redundant
        if None in links:
            links.remove(None)
        if "" in links:
            links.remove("")
        if "http" in links:
            links.remove("http")
        if "https" in links:
            links.remove("https")
        if "http://" in links:
            links.remove("http://")
        if "https://" in links:
            links.remove("https://")

        return links

    def get_links_inner(self):
        links = self.get_links()
        links = ContentLinkParser.filter_link_html(links)
        return ContentLinkParser.filter_link_in_domain(
            links, UrlLocation(self.url).get_domain()
        )

    def get_links_outer(self):
        links = self.get_links()
        links = ContentLinkParser.filter_link_html(links)

        in_domain = ContentLinkParser.filter_link_in_domain(
            links, UrlLocation(self.url).get_domain()
        )
        return links - in_domain
