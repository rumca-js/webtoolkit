"""
Crawler interface can be implemented to provide new mechanisms of crawling
"""

import threading
import traceback
import ua_generator

from webtoolkit import (
    PageRequestObject,
    PageResponseObject,
    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_EXCEPTION
)


def get_default_headers(device=None, browser=None):
    if not device:
        device = "desktop"
    if not browser:
        browser = ["chrome", "edge"]

    ua = ua_generator.generate(device=device, browser=browser)
    headers = ua.headers.get()

    if "user-agent" in headers:
        headers["User-Agent"] = headers["user-agent"]
        del headers["user-agent"]

    return headers


def get_default_user_agent(device=None, browser=None):
    headers = get_default_headers(device, browser)
    if "User-Agent" in headers:
        return headers["User-Agent"]


class WebToolsTimeoutException(Exception):
    """Custom exception to indicate a request timeout."""

    def __init__(self, message="The request has timed out."):
        super().__init__(message)


class CrawlerInterface(object):
    """
    Crawler is a tool that allows to obtain contents from the internet.
    There are various tools.
    """

    def __init__(self, url=None, request=None, verbose=False):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        if not request:
            request = PageRequestObject(url)

        self.request = request
        self.response = None
        self.errors = []
        self.verbose = verbose

    def update_request(self):
        """
        Should be implemented by crawler - whatever is uses to perform request
        """
        pass

    def set_url(self, url):
        self.request.url = url

    def make_request(self, request):
        self.request = request

    def run(self):
        """
        Prepares for request, runs request, prepares response.
         - does its job
         - sets self.response
         - we should be able to call run several times

        @return response (always, but may be invalid)
        """

        # by default it is our error that no valid data were returned
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        try:
            self.response = self.run_internal()
        except Exception as E:
            self.add_exc(E)

        return self.get_response()

    def set_timeout_response(self):
        self.response.status_code = HTTP_STATUS_CODE_TIMEOUT
        self.add_error(f"Url:{self.request.url} Timout")

    def set_connection_error_response(self):
        self.response.status_code = HTTP_STATUS_CODE_CONNECTION_ERROR
        self.add_error(f"Url:{self.request.url} Connection error")

    def set_exception_response(self, E):
        self.response.status_code = HTTP_STATUS_CODE_EXCEPTION
        self.add_exc(E)

    def get_response(self):
        """
        Returns finished response
        """
        if self.response:
            self.response.request = self.request
            self.response.errors = self.errors
            return self.response

    def run_internal(self):
        """
        Runs request only
         - does its job
         - sets self.response
         - we should be able to call run several times, for various requests

        @return response (always, but may be invalid)
        """
        return self.response

    def get_default_user_agent(self):
        return get_default_user_agent()

    def get_default_headers(self):
        return get_default_headers()

    def add_error(self, error):
        self.errors.append(error)

    def add_exc(self, exc):
        if exc is None:
            self.add_error("Attempt to add none as exception")
            return

        error_text = traceback.format_exc()

        stack_lines = traceback.format_stack()
        stack_string = "".join(stack_lines)

        text = f"Url:{self.request.url} Exception:"
        text += str(exc) + "\r\n" + error_text + "\r\n" + stack_string

        self.errors.append(text)

    def is_response_valid(self):
        if not self.response:
            return False

        if not self.response.is_valid():
            self.add_error(
                f"Response not valid. Status:{self.response.status_code}"
            )
            return False

        content_length = self.response.get_content_length()
        bytes_limit = self.get_bytes_limit()

        if content_length is not None and bytes_limit is not None:
            if content_length > bytes_limit:
                self.add_error("Page is too big: ".format(content_length))
                return False

        content_type = self.response.get_content_type_keys()
        content_type_keys = self.response.get_content_type_keys()
        if content_type_keys:
            if "all" in self.get_accept_types():
                return True

            match_count = 0
            for item in content_type_keys:
                if item in self.get_accept_types():
                    match_count += 1

            if match_count == 0:
                self.add_error(
                    "Response type is not supported:{}".format(content_type)
                )
                return False

        return True

    def is_valid(self):
        return False

    def close(self):
        self.request = None
        self.response = None

    def get_accept_types(self):
        accept_string = self.request.accept_types
        if not accept_string:
            accept_string = "all"

        semicolon_index = accept_string.find(";")
        if semicolon_index >= 0:
            accept_string = accept_string[:semicolon_index]

        result = set()
        # Split by comma to separate media types
        media_types = accept_string.split(",")
        for media in media_types:
            # Further split each media type by '/' and '+'
            parts = media.strip().replace("+", "/").split("/")
            for part in parts:
                if part:
                    result.add(part.strip())

        return list(result)

    def get_request_headers(self):
        headers = self.request.request_headers
        custom_user_agent = self.request.user_agent

        if not headers or len(headers) == 0:
            headers = self.get_default_headers()

        if custom_user_agent:
            headers["User-Agent"] = custom_user_agent

        if "User-Agent" not in headers:
            headers["User-Agent"] = self.get_default_user_agent()

        return headers

    def get_user_agent(self):
        headers = self.request.request_headers
        custom_user_agent = self.request.user_agent

        if custom_user_agent:
            return custom_user_agent

        return self.get_default_user_agent()

    def get_timeout_s(self):
        timeout_s = self.request.timeout_s

        if timeout_s is not None:
            return timeout_s

        return 20

    def get_bytes_limit(self):
        bytes_limit = self.request.bytes_limit
        return bytes_limit

    def get_response_file(self):
        if self.request.settings:
            real_settings = self.request.settings

            response_file = real_settings.get("response_file")
            return response_file

    def build_requests(self):
        """
        Perform an HTTP GET request with total timeout control using threading.

        Notes:
        - stream=True defers the content download until accessed.
        - Overcomes the limitation of requests.get's timeout (which doesn't cover total duration).
        """

        def crawl_with_thread_wrapper(request, result):
            try:
                result["response"] = self.crawl_with_thread_implementation(request)
            except Exception as e:
                result["exception"] = e

        def crawl_with_thread(request):
            result = {"response": None, "exception": None}

            thread = threading.Thread(
                target=crawl_with_thread_wrapper,
                args=(request, result),
                daemon=True,
            )

            thread.start()

            # give additional wait time
            # requests (or other mechanisms) sohuld timeout first
            # give it some 'time space' to timeout gracefully
            thread.join(request.timeout_s + 5)

            if thread.is_alive():
                raise WebToolsTimeoutException("Request timed out")
            if result["exception"]:
                raise result["exception"]
            return result["response"]

        self.update_request()

        response = crawl_with_thread(
            request=self.request,
        )
        return response

    def crawl_with_thread_implementation(self, request):
        """
        To be implemented
        """
        pass
