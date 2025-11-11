"""
Main Url handling class

@example
url = Url(link = "https://google.com")
response = url.get_response()

options.request.url
options.mode_mapping

"""

import urllib.robotparser
import asyncio

from webtoolkit import (
    UrlLocation,
    BaseUrl,
)

from webtoolkit.utils.dateutils import DateUtils


class DomainCacheInfo(object):
    """
    is_access_valid
    """

    def __init__(self, url, respect_robots_txt=True, request=None, url_builder=None):
        p = UrlLocation(url)

        self.respect_robots_txt = respect_robots_txt

        self.url = p.get_domain()
        self.robots_contents = None
        self.request = request
        self.url_builder = url_builder

        if not self.url_builder:
            self.url_builder = BaseUrl

        if self.respect_robots_txt:
            self.robots_contents = self.get_robots_txt_contents()
            self.robots = self.get_robots_txt()

    def is_allowed(self, url):
        if self.respect_robots_txt and self.robots:
            user_agent = "*"
            return self.robots.can_fetch(user_agent, url)
        else:
            return True

    def get_robots_txt_url(self):
        p = UrlLocation(self.url)
        return p.get_robots_txt_url()

    def get_robots_txt(self):
        """
        https://developers.google.com/search/docs/crawling-indexing/robots/intro
        """
        contents = self.get_robots_txt_contents()
        if contents:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(self.get_robots_txt_url())
            rp.parse(contents.split("\n"))
            return rp

    def is_robots_txt(self):
        return self.get_robots_txt_contents()

    def get_robots_txt_contents(self):
        """
        We can only ask domain for robots
        """
        if self.robots_contents:
            return self.robots_contents

        robots_url = self.get_robots_txt_url()
        u = self.url_builder(robots_url, request=self.request)

        response = u.get_response()
        if response:
            self.robots_contents = response.get_text()

        return self.robots_contents

    def get_site_maps_urls(self):
        """
        https://stackoverflow.com/questions/2978144/pythons-robotparser-ignoring-sitemaps
        robot parser does not work. We have to do it manually
        """
        result = set()

        contents = self.get_robots_txt_contents()
        if contents:
            lines = contents.split("\n")
            for line in lines:
                line = line.replace("\r", "")
                wh = line.find("Sitemap")
                if wh >= 0:
                    wh2 = line.find(":")
                    if wh2 >= 0:
                        sitemap = line[wh2 + 1 :].strip()
                        result.add(sitemap)

        return list(result)

    def get_site_urls(self):
        result = []

        contents = self.get_robots_txt_contents()
        if contents:
            lines = contents.split("\n")
            for line in lines:
                if line.find("Disallow") >= 0 or line.find("Allow") >= 0:
                    link = process_allow_link(line)
                    result.append(link)

        urls = self.get_site_maps_urls()
        for url in urls:
            u = slef.url_builder(url=url, request=self.request)
            response = u.get_response()
            contents = response.get_text()
            if contents:
                parser = ContentLinkParser(url, contents)
                parser = ContentLinkParser(self.url, contents)
                links = parser.get_links()

                result.extend(links)

        return result

    def process_allow_link(self, line):
        wh = line.find(":")
        if wh >= 0:
            part = line[wh + 1 :].strip()
            # robots can have wildcards, we cannot now what kind of location it is
            if part.find("*") == -1:
                return self.url + part

    def get_all_site_maps_urls(self):
        sites = set(self.get_site_maps_urls())

        for site in sites:
            subordinate_sites = self.get_subordinate_sites(site)
            sites.update(subordinate_sites)

        return list(sites)

    def get_subordinate_sites(self, site):
        all_subordinates = set()

        u = self.url_builder(site, request=self.request)
        response = u.get_response
        if not response:
            return all_subordinates

        contents = response.get_text()

        # check if it is sitemap / sitemap index
        # https://www.sitemaps.org/protocol.html#index
        if contents.find("<urlset") == -1 and contents.find("<sitemapindex") == -1:
            return all_subordinates

        p = ContentLinkParser(self.url, contents)
        links = p.get_links()

        for link in links:
            subordinates = self.get_subordinate_sites(link)
            all_subordinates.update(subordinates)

        return all_subordinates


class DomainCache(object):
    """
    DomainCache.get_object("https://youtube.com/mysite/something").is_allowed("url")
    Url().get_domain_cache().is_allowed()
    """

    object = None  # singleton
    default_cache_size = 400
    respect_robots_txt = True

    def get_object(domain_url, request=None, url_builder=None):
        if DomainCache.object is None:
            DomainCache.object = DomainCache(
                DomainCache.default_cache_size,
                request=request,
                url_builder=url_builder,
            )

        return DomainCache.object.get_domain_info(domain_url)

    def __init__(
        self,
        cache_size=400,
        respect_robots_txt=True,
        request=None,
        url_builder=None,
    ):
        """
        @note Not public
        """
        self.cache_size = cache_size
        self.cache = {}
        self.respect_robots_txt = respect_robots_txt
        self.request = request
        self.url_builder = url_builder

    def get_domain_info(self, input_url):
        domain_url = UrlLocation(input_url).get_domain_only()

        if not domain_url in self.cache:
            self.remove_from_cache()
            self.cache[domain_url] = {
                "date": DateUtils.get_datetime_now_utc(),
                "domain": self.read_info(domain_url),
            }

        return self.cache[domain_url]["domain"]

    def read_info(self, domain_url):
        return DomainCacheInfo(
            domain_url,
            self.respect_robots_txt,
            request=self.request,
            url_builder=self.url_builder,
        )

    def remove_from_cache(self):
        if len(self.cache) < self.cache_size:
            return

        thelist = []
        for domain in self.cache:
            info = self.cache[domain]
            thelist.append([domain, info["date"], info["domain"]])

        thelist.sort(key=lambda x: x[1])
        thelist = thelist[-self.cache_size : -1]

        self.cache.clear()

        for item in thelist:
            self.cache[item[0]] = {"date": item[1], "domain": item[2]}
