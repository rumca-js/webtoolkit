"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import time
import threading

from ..pages import RssPage, HtmlPage
from ..response import PageResponseObject, file_to_response
from .crawlerinterface import CrawlerInterface
from ..webconfig import WebLogger
from ..statuses import (
    HTTP_STATUS_UNKNOWN,
    HTTP_STATUS_OK,
    HTTP_STATUS_USER_AGENT,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)
from .crawlerinterface import WebToolsTimeoutException


class RequestsCrawler(CrawlerInterface):
    """
    Python requests are based.

    Quirks:
     - timeout in requests defines timeout for stalled communication.
       this means you can be stuck if you read 1byte/second.
       This means we have to start a thread, and make timeout ourselves
    """

    def run(self):
        if not self.is_valid():
            return

        import requests

        WebLogger.debug("Requests Driver:{}".format(self.request.url))

        """
        stream argument allows us to read header before we fetch the page.
        SSL verification makes everything to work slower.
        """

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        try:
            request_result = self.build_requests()

            if request_result is None:
                self.response.add_error("Could not build response")
                return self.response

            self.response = PageResponseObject(
                url=request_result.url,
                text=None,
                status_code=request_result.status_code,
                headers=dict(request_result.headers),
                request_url=self.request.url,
            )
            if not self.is_response_valid():
                request_result.close()

                return self.response

            if self.request.request_type == "ping":
                request_result.close()
                return self.response

            # TODO do we want to check also content-type?

            content_type = self.response.get_content_type()

            if content_type and not self.response.is_content_type_text():
                self.response.binary = request_result.content
                request_result.close()
                return self.response
            else:
                encoding = self.get_encoding(self.response, request_result)
                if encoding:
                    request_result.encoding = encoding

                self.response = PageResponseObject(
                    url=request_result.url,
                    text=request_result.text,
                    status_code=request_result.status_code,
                    encoding=request_result.encoding,
                    headers=dict(request_result.headers),
                    binary=request_result.content,
                    request_url=self.request.url,
                )

                request_result.close()

        except requests.Timeout:
            WebLogger.debug("Url:{} timeout".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except WebToolsTimeoutException:
            WebLogger.debug("Url:{} timeout".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except requests.exceptions.ConnectionError:
            WebLogger.debug("Url:{} connection error".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(self.request.url))

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("General page exception: {}".format(str(E)))

        return self.response

    def get_encoding(self, response, request_result):
        """
        The default assumed content encoding for text/html is ISO-8859-1 aka Latin-1 :( See RFC-2854. UTF-8 was too young to become the default, it was born in 1993, about the same time as HTML and HTTP.
        Use .content to access the byte stream, or .text to access the decoded Unicode stream.

        chardet does not work on youtube RSS feeds.
        apparent encoding does not work on youtube RSS feeds.
        """

        url = self.request.url

        encoding = response.get_encoding()
        if encoding:
            return encoding

        else:
            text = request_result.text
            # There might be several encoding texts, if so we do not know which one to use
            if response.is_content_html():
                p = HtmlPage(url, text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()
            if response.is_content_rss():
                p = RssPage(url, text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()

            # TODO this might trigger download of a big file
            text = text.lower()

            if text.count("encoding") == 1 and text.find('encoding="utf-8"') >= 0:
                return "utf-8"
            elif text.count("charset") == 1 and text.find('charset="utf-8"') >= 0:
                return "utf-8"

    def make_requests_call(self, request, stream):
        """
        This method can be overridden in subclasses to change the request behavior.
        """
        import requests

        return requests.get(
            request.url,
            headers=request.request_headers,
            timeout=request.timeout_s,
            verify=request.ssl_verify,
            cookies=request.cookies,
            stream=stream,
        )

    def build_requests(self):
        """
        Perform an HTTP GET request with total timeout control using threading.

        Notes:
        - stream=True defers the content download until accessed.
        - Overcomes the limitation of requests.get's timeout (which doesn't cover total duration).
        """

        def request_with_timeout(request, stream, result):
            try:
                result["response"] = self.make_requests_call(
                    request, stream
                )
            except Exception as e:
                result["exception"] = e

        def make_request_with_threading(request, stream):
            result = {"response": None, "exception": None}

            thread = threading.Thread(
                target=request_with_timeout,
                args=(request, stream, result),
            )
            thread.start()
            thread.join(request.timeout_s)

            if thread.is_alive():
                raise WebToolsTimeoutException("Request timed out")
            if result["exception"]:
                raise result["exception"]
            return result["response"]

        self.request.headers = self.get_request_headers()
        self.request.timeout_s = self.get_timeout_s()

        response = make_request_with_threading(
            request=self.request,
            stream=True,
        )
        return response

    def is_valid(self):
        try:
            import requests

            return True
        except Exception as E:
            print(str(E))
            return False

    def ping(self):
        import requests

        user_agent = self.get_user_agent()
        headers = self.get_default_headers()
        headers["User-Agent"] = user_agent
        url = self.request.url

        response = None
        try:
            with requests.get(
                url=url,
                headers=headers,
                timeout=20,
                verify=False,
                stream=True,
            ) as response:
                response = PageResponseObject(
                    url,
                    text=None,
                    status_code=response.status_code,
                    request_url=url,
                )

        except requests.Timeout:
            WebLogger.debug("Url:{} timeout".format(url))
            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=url,
            )

        except requests.exceptions.ConnectionError:
            WebLogger.debug("Url:{} connection error".format(url))
            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=url,
            )

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(url))

            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=url,
            )

        return response
