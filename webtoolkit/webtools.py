"""
This file should not include any other or django related files.

#1
Do not harm anyone. Write ethical programs, and scrapers.

#2
By default SSL verification is disabled. Speeds up processing. At least in my experience.

SSL is mostly important for interacting with pages, not when web scraping. I think. I am not an expert.

#3
If SSL verification is disabled you can see contents of your own domain:
https://support.bunny.net/hc/en-us/articles/360017484759-The-CDN-URLs-are-returning-redirects-back-to-my-domain

Other notes:
 - Sometimes we see the CDN URLs return a 301 redirect back to your own website.
   Usually, when this happens, it's caused by a misconfiguration of your origin server and the origin URL of your pull zone. If the origin URL sends back a redirect, our servers will simply forward that to the user.
 - 403 status code means that your user agent is incorrect / prohibited
 - other statuses can also mean that your user agent is rejected (rarely / edge cases)
 - content-type in headers can be incorrectly set. Found one RSS file that had "text/html"
 - I rely on tools. Those tools have problems/issues. Either we can live with that, or you would have to implement every dependency

TODO:
    - selenium and other drivers should be created once, then only asked for urls. Currently they are re-created each time we ask for a page
    - currently there is a hard limit for file size. If page is too big, it is just skipped
    - we should check meta info before obtaining entire file. Currently it is not done so. Encoding may be read from file, in some cases
    - maybe lists of mainstream media, or link services could be each in one class. Configurable, so that it can be overriden

Main classes are:
    - Url - most things should be done through it
    - PageOptions - upper layers should decide how a page should be called. Supplied to Url
    - PageRequestObject - request
    - PageResponseObject - page response, interface for all implementations
"""

import base64
import hashlib
import html
import json
import re
import traceback
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Optional, Type

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from dateutil import parser

from .utils.dateutils import DateUtils

__version__ = "0.0.5"


URL_TYPE_RSS = "rss"
URL_TYPE_CSS = "css"
URL_TYPE_JAVASCRIPT = "javascript"
URL_TYPE_HTML = "html"
URL_TYPE_FONT = "font"
URL_TYPE_UNKNOWN = "unknown"


class WebLogger(object):
    """
    A simple logging interface that directs log messages to a configurable logger.
    This class provides a set of static methods for logging at different levels (info, debug, warning, error)
    and for logging exceptions. The actual logging is delegated to the `web_logger` object,
    if it is set.
    """

    web_logger = None

    @staticmethod
    def info(info_text, detail_text="", user=None, stack=False):
        """
        Logs an informational message.
        :param info_text: The main informational text to log.
        :param detail_text: Additional details for the log message.
        :param user: The user associated with the log event.
        :param stack: If True, include stack information in the log.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.info(info_text, detail_text, user, stack)

    @staticmethod
    def debug(info_text, detail_text="", user=None, stack=False):
        """
        Logs a debug message.
        :param info_text: The main debug text to log.
        :param detail_text: Additional details for the log message.
        :param user: The user associated with the log event.
        :param stack: If True, include stack information in the log.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.debug(info_text, detail_text, user, stack)

    @staticmethod
    def warning(info_text, detail_text="", user=None, stack=False):
        """
        Logs a warning message.
        :param info_text: The main warning text to log.
        :param detail_text: Additional details for the log message.
        :param user: The user associated with the log event:
        :param stack: If True, include stack information in the log.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.warning(info_text, detail_text, user, stack)

    @staticmethod
    def error(info_text, detail_text="", user=None, stack=False):
        """
        Logs an error message.
        :param info_text: The main error text to log.
        :param detail_text: Additional details for the log message.
        :param user: The user associated with the log event.
        :param stack: If True, include stack information in the log.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.error(info_text, detail_text, user, stack)

    @staticmethod
    def notify(info_text, detail_text="", user=None):
        """
        Sends a notification.
        :param info_text: The main notification text.
        :param detail_text: Additional details for the notification.
        :param user: The user associated with the notification.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.notify(info_text, detail_text, user, stack)

    @staticmethod
    def exc(exception_object, info_text=None, user=None):
        """
        Logs an exception.
        :param exception_object: The exception object to log.
        :param info_text: Additional informational text to accompany the exception.
        :param user: The user associated with the exception event.
        """
        if WebLogger.web_logger:
            WebLogger.web_logger.exc(exception_object, info_text)


def lazy_load_content(func):
    """
    A decorator that delays the loading of content until it is actually needed.
    This is used to prevent fetching page content during the construction of an object,
    deferring it until a method that requires the content is called.
    :param func: The function to wrap.
    :return: The wrapped function.
    """

    def wrapper(self, *args, **kwargs):
        if not self.response:
            self.response = self.get_response()
        return func(self, *args, **kwargs)

    return wrapper


def date_str_to_date(date_str):
    """
    Converts a date string into a timezone-aware datetime object.
    The function can handle various date formats and cleans the string if it contains "Published:" prefix.
    :param date_str: The date string to parse.
    :return: A datetime object converted to UTC, or None if parsing fails.
    """
    if date_str:
        wh = date_str.find("Published:")
        if wh >= 0:
            wh = date_str.find(":", wh)
            date_str = date_str[wh + 1 :].strip()

        try:
            parsed_date = parser.parse(date_str)
            return DateUtils.to_utc_date(parsed_date)
        except Exception as E:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            # we want to know who generated this issue
            detail_text = "Exception Data:{}\nStack:{}".format(str(E), stack_str)

            WebLogger.info(
                "Could not parse date:{}\n".format(date_str),
                detail_text=detail_text,
            )


def calculate_hash(text):
    """
    Calculates the MD5 hash of a given text.
    :param text: The text to hash.
    :return: The MD5 hash as bytes, or None if the input text is empty.
    """
    if not text:
        return
    try:
        return hashlib.md5(text.encode("utf-8")).digest()
    except Exception as E:
        WebLogger.exc(E, "Could not calculate hash")


def calculate_hash_binary(binary):
    """
    Calculates the MD5 hash of a given binary data.
    :param binary: The binary data to hash.
    :return: The MD5 hash as bytes, or None if the input binary data is empty.
    """
    if not binary:
        return
    try:
        return hashlib.md5(binary).digest()
    except Exception as E:
        WebLogger.exc(E, "Could not calculate hash")


class InputContent(object):
    """
    A class for processing and transforming input text, particularly for handling HTML content.
    It provides methods to linkify URLs and strip unwanted HTML attributes.
    """

    def __init__(self, text: str):
        """
        Initializes the InputContent object with the given text.
        :param text: The input text to process.
        """
        self.text = text

    def htmlify(self) -> str:
        """
        Converts plain text URLs in the content into clickable HTML links.
        This method first strips unwanted HTML attributes and then linkifies "https://" and "http://" URLs.
        :return: The processed text with HTML links.
        """
        self.text = self.strip_html_attributes()
        self.text = self.linkify("https://")
        self.text = self.linkify("http://")
        return self.text

    def strip_html_attributes(self) -> str:
        """
        Strips all HTML attributes from tags, except for 'href' in 'a' tags and 'src' in 'img' tags.
        :return: The text with unwanted HTML attributes removed.
        """
        soup = BeautifulSoup(self.text, "html.parser")

        for tag in soup.find_all(True):
            if tag.name == "a":
                # Preserve "href" attribute for anchor tags
                tag.attrs = {"href": tag.get("href")}
            elif tag.name == "img":
                # Preserve "src" attribute for image tags
                tag.attrs = {"src": tag.get("src")}
            else:
                # Remove all other attributes
                tag.attrs = {}

        self.text = str(soup)
        return self.text

    def linkify(self, protocol: str = "https://") -> str:
        """
        Finds URLs starting with the given protocol and wraps them in an HTML 'a' tag.
        It avoids wrapping URLs that are already inside an 'a' or 'img' tag.
        :param protocol: The protocol to look for (e.g., "https://").
        :return: The text with URLs converted to HTML links.
        """
        if self.text.find(protocol) == -1:
            return self.text

        result = ""
        i = 0

        while i < len(self.text):
            pattern = r"{}\S+(?![\w.])".format(re.escape(protocol))
            match = re.search(pattern, self.text[i:])
            if match:
                url = match.group(0)
                start_index = i + match.start()
                end_index = i + match.end()

                # Check the previous 10 characters
                preceding_chars = self.text[max(0, start_index - 10) : start_index]

                result += self.text[i:start_index]

                # We do not care who write links using different char order
                if '<a href="' not in preceding_chars and "<img" not in preceding_chars:
                    result += f'<a href="{url}">{url}</a>'
                else:
                    result += url
                i = end_index
            else:
                result += self.text[i:]
                break

        self.text = result
        return result


def json_encode_field(byte_property: bytes) -> Optional[str]:
    """
    Encodes a byte string into a base64 UTF-8 string.
    :param byte_property: The byte string to encode.
    :return: The base64-encoded string, or None if the input is empty.
    """
    if not byte_property:
        return

    return base64.b64encode(byte_property).decode("utf-8")


def json_decode_field(data: str) -> Optional[bytes]:
    """
    Decodes a base64 string into a byte string.
    :param data: The base64 string to decode.
    :return: The decoded byte string, or None if the input is empty.
    """
    if not data:
        return

    return base64.b64decode(data)
