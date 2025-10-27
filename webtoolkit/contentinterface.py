"""
Provides interface and page types Html, RSS, JSON etc.
"""

from time import strptime
import re
from datetime import datetime
from dateutil import parser

from .utils.dateutils import DateUtils

from .webtools import (
    calculate_hash,
    WebLogger,
)
from .urllocation import UrlLocation


class ContentInterface(object):
    def __init__(self, url, contents):
        self.url = url
        self.contents = contents

    def get_contents(self):
        return self.contents

    def get_title(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError

    def get_language(self):
        raise NotImplementedError

    def get_thumbnail(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def get_album(self):
        raise NotImplementedError

    def get_tags(self):
        raise NotImplementedError

    def get_url(self):
        return self.url

    def get_canonical_url(self):
        return self.url

    def get_feeds(self):
        return []

    def get_page_rating(self):
        """
        Default behavior
        """
        rating_vector = self.get_page_rating_vector()
        link_rating = self.get_link_rating()
        rating_vector.extend(link_rating)

        page_rating = 0
        max_page_rating = 0
        for rating in rating_vector:
            page_rating += rating[0]
            max_page_rating += rating[1]

        if page_rating == 0:
            return 0
        if max_page_rating == 0:
            return 0

        page_rating = (float(page_rating) * 100.0) / float(max_page_rating)

        try:
            return int(page_rating)
        except ValueError:
            return 0

    def get_page_rating_vector(self):
        """
        Returns vector of tuples.
        Each tuple contains actual rating for property, and max rating for that property
        """
        result = []

        if self.get_title() is not None and str(self.get_title()) != "":
            result.append([10, 10])

        if self.get_description() is not None and str(self.get_description()) != "":
            result.append([5, 5])

        if self.get_language() is not None and str(self.get_language()) != "":
            result.append([1, 1])

        if self.get_thumbnail() is not None and str(self.get_thumbnail()) != "":
            result.append([1, 1])

        if (
            self.get_date_published() is not None
            and str(self.get_date_published()) != ""
        ):
            result.append([1, 1])

        return result

    def get_date_published(self):
        """
        This should be date. Not string
        """
        raise NotImplementedError

    def get_contents_hash(self):
        contents = self.get_contents()
        if contents:
            return calculate_hash(contents)

    def get_contents_body_hash(self):
        return self.get_contents_hash()

    def get_properties(self):
        props = {}

        props["link"] = self.url
        props["title"] = self.get_title()
        props["description"] = self.get_description()
        props["author"] = self.get_author()
        props["album"] = self.get_album()
        props["thumbnail"] = self.get_thumbnail()
        props["language"] = self.get_language()
        props["page_rating"] = self.get_page_rating()
        props["date_published"] = self.get_date_published()
        props["tags"] = self.get_tags()
        props["link_canonical"] = self.get_canonical_url()

        return props

    def is_captcha_protected(self):
        """
        Should not obtain contents by itself

        You'd probably be more successful trying to not trigger
        the bot detection in the first place rather than trying to bypass it after the fact.

        https://github.com/ZA1815/caniscrape/blob/main/caniscrape/analyzers/captcha_detector.py
        """

        CAPTCHA_FINGERPRINTS = {
            "reCAPTCHA": ["google.com/recaptcha", "recaptcha/api.js", "g-recaptcha"],
            "hCaptcha": ["hcaptcha.com", "hcaptcha-box", "h-captcha"],
            "Cloudflare Turnstile": [
                "challenges.cloudflare.com/turnstile",
                "cf-turnstile",
            ],
        }

        contents = self.contents

        if contents:
            for provider, patterns in CAPTCHA_FINGERPRINTS.items():
                for pattern in patterns:
                    if contents.find(pattern) >= 0:
                        return True

        return False

    def guess_date(self):
        """
        This is ugly, but dateutil.parser does not work. May generate exceptions.
        Ugly is better than not working.

        Supported formats:
         - Jan. 15, 2024
         - Jan 15, 2024
         - January 15, 2024
         - 15 January 2024 14:48 UTC
        """

        content = self.get_contents()
        if not content:
            return

        # searching will be case insensitive
        content = content.lower()

        # Get the current year
        try:
            current_year = int(datetime.now().year)
        except ValueError:
            # TODO fix this
            current_year = 2024

        # Define regular expressions
        current_year_pattern = re.compile(rf"\b{current_year}\b")
        four_digit_number_pattern = re.compile(r"\b\d{4}\b")

        # Attempt to find the current year in the string
        match_current_year = current_year_pattern.search(content)

        year = None
        scope = None

        if match_current_year:
            try:
                year = int(current_year)
            except ValueError:
                # TODO fix this
                year = 2024

            # Limit the scope to a specific portion before and after year
            scope = content[
                max(0, match_current_year.start() - 15) : match_current_year.start()
                + 20
            ]
        else:
            match_four_digit_number = four_digit_number_pattern.search(content)
            if match_four_digit_number:

                try:
                    year = int(match_four_digit_number.group(0))

                    # Limit the scope to a specific portion before and after year
                    scope = content[
                        max(
                            0, match_four_digit_number.start() - 15
                        ) : match_four_digit_number.start()
                        + 20
                    ]
                except ValueError:
                    return

        if scope:
            return self.guess_by_scope(scope, year)

    def guess_by_scope(self, scope, year):
        date_pattern_iso = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")

        month_re = "(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"

        # 2024 jan 23
        date_pattern_us = re.compile(
            r"(\d{4})\s*{}\s*(\d{1,2})".replace("{}", month_re)
        )
        # jan 23 2024
        date_pattern_us2 = re.compile(
            r"{}\s*(\d{1,2})\s*(\d{4})".replace("{}", month_re)
        )
        # 23 jan 2024
        date_pattern_ue = re.compile(
            r"(\d{1,2})\s*{}\s*(\d{4})".replace("{}", month_re)
        )

        # only Jan 23, without year next by
        month_date_pattern = re.compile(r"\b{}\s*(\d+)\b".replace("{}", month_re))

        date_pattern_iso_match = date_pattern_iso.search(scope)
        date_pattern_us_match = date_pattern_us.search(scope)
        date_pattern_us2_match = date_pattern_us2.search(scope)
        date_pattern_ue_match = date_pattern_ue.search(scope)

        month_date_pattern_match = month_date_pattern.search(scope)

        date_object = None

        if date_pattern_iso_match:
            year, month, day = date_pattern_iso_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_us_match:
            year, month, day = date_pattern_us_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_us2_match:
            month, day, year = date_pattern_us2_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_ue_match:
            day, month, year = date_pattern_ue_match.groups()
            date_object = self.format_date(year, month, day)

        # If a month and day are found, construct a datetime object with year, month, and day
        elif month_date_pattern_match:
            month, day = month_date_pattern_match.groups()
            date_object = self.format_date(year, month, day)

        # elif year:
        #    current_year = int(datetime.now().year)

        #    if year >= current_year or year < 1900:
        #        date_object = datetime.now()
        #    else:
        #        # If only the year is found, construct a datetime object with year
        #        date_object = datetime(year, 1, 1)

        # For other scenario to not provide any value

        if date_object:
            date_object = DateUtils.to_utc_date(date_object)

        return date_object

    def format_date(self, year, month, day):
        month_number = None

        try:
            month_number = int(month)
            month_number = month
        except ValueError as E:
            WebLogger.debug("Error:{}".format(str(E)))

        if not month_number:
            try:
                month_number = strptime(month, "%b").tm_mon
                month_number = str(month_number)
            except Exception as E:
                WebLogger.debug("Error:{}".format(str(E)))

        if not month_number:
            try:
                month_number = strptime(month, "%B").tm_mon
                month_number = str(month_number)
            except Exception as E:
                WebLogger.debug("Error:{}".format(str(E)))

        if month_number is None:
            WebLogger.debug(
                "Guessing date error: URL:{};\nYear:{};\nMonth:{}\nDay:{}".format(
                    self.url, year, month, day
                )
            )
            return

        try:
            date_object = datetime.strptime(
                f"{year}-{month_number.zfill(2)}-{day.zfill(2)}", "%Y-%m-%d"
            )

            return date_object
        except Exception as E:
            WebLogger.debug(
                "Guessing date error: URL:{};\nYear:{};\nMonth:{}\nDay:{}".format(
                    self.url, year, month, day
                )
            )

    def get_position_of_html_tags(self):
        if not self.contents:
            return -1

        lower = self.contents.lower()
        if lower.find("<html") >= 0 and lower.find("<body") >= 0:
            return lower.find("<html")

        lower = self.contents.lower()
        if lower.find("<html") >= 0 and lower.find("<meta") >= 0:
            return lower.find("<html")

        return -1

    def get_position_of_rss_tags(self):
        if not self.contents:
            return -1

        lower = self.contents.lower()
        if lower.find("<rss") >= 0 and lower.find("<channel") >= 0:
            return lower.find("<rss")
        if lower.find("<feed") >= 0 and lower.find("<entry") >= 0:
            return lower.find("<feed")
        if lower.find("<rdf") >= 0 and lower.find("<channel") >= 0:
            return lower.find("<rdf")

        return -1

    def get_link_rating(self):
        rating = []

        if self.url.startswith("https://"):
            rating.append([1, 1])
        elif self.url.startswith("ftp://"):
            rating.append([1, 1])
        elif self.url.startswith("smb://"):
            rating.append([1, 1])
        elif self.url.startswith("http://"):
            rating.append([0, 1])
        else:
            rating.append([0, 1])

        p = UrlLocation(self.url)
        if p.is_domain():
            rating.append([1, 1])

        domain_only = p.get_domain_only()
        if not domain_only:
            rating.append([0, 2])
        elif domain_only.count(".") == 1:
            rating.append([2, 2])
        elif domain_only.count(".") == 2:
            rating.append([1, 2])
        else:
            rating.append([0, 2])

        # as example https://www.youtube.com has 23 chars

        if len(self.url) < 25:
            rating.append([2, 2])
        elif len(self.url) < 30:
            rating.append([1, 2])
        else:
            rating.append([0, 2])

        return rating
