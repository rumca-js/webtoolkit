"""
"""

import html
import json
import base64
from collections import OrderedDict

from .webtools import (
    calculate_hash,
    calculate_hash_binary,
    json_encode_field,
    json_decode_field,
    date_str_to_date,
    WebLogger,
)
from .statuses import *
from utils.dateutils import DateUtils


class ResponseHeaders(object):
    def __init__(self, headers):
        self.headers = dict(headers)

    def get(self, field):
        return self.headers.get(field)

    def is_headers_empty(self):
        return len(self.headers) == 0

    def get_content_type(self):
        if "Content-Type" in self.headers:
            return self.headers["Content-Type"]
        if "content-type" in self.headers:
            return self.headers["content-type"]

    def get_content_type_keys(self):
        content_type = self.get_content_type()
        if content_type:
            semicolon = content_type.find(";")
            if semicolon >= 0:
                content_type = content_type[:semicolon]
            content_type = content_type.replace("+", "/")
            return content_type.split("/")

    def get_last_modified(self):
        date = None

        if "Last-Modified" in self.headers:
            date = self.headers["Last-Modified"]
        if "last-modified" in self.headers:
            date = self.headers["last-modified"]

        if date:
            return date_str_to_date(str(date))

    def get_clean_headers(self):
        self.headers["Content-Type"] = self.get_content_type()
        self.headers["Content-Length"] = self.get_content_length()
        self.headers["Last-Modified"] = self.get_last_modified()
        self.headers["Charset"] = self.get_content_type_charset()

        return self.headers

    def get_encoding(self):
        if not self.is_headers_empty():
            charset = self.get_content_type_charset()
            if charset:
                return charset

    def get_default_encoding(self):
        return "utf-8"

    def get_content_type_charset(self):
        content = self.get_content_type()
        if not content:
            return

        elements = content.split(";")
        for element in elements:
            wh = element.lower().find("charset")
            if wh >= 0:
                charset_elements = element.split("=")
                if len(charset_elements) > 1:
                    charset = charset_elements[1]

                    if charset.startswith('"') or charset.startswith("'"):
                        return charset[1:-1]
                    else:
                        return charset

    def is_content_html(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("html") >= 0:
            return True

    def is_content_image(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("image") >= 0:
            return True

    def is_content_rss(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("rss") >= 0:
            return True
        if content.lower().find("xml") >= 0:
            return True

    def is_content_json(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("json") >= 0:
            return True

    def get_content_length(self):
        content_len = None
        if "content-length" in self.headers:
            content_len = self.headers["content-length"]
        if "Content-Length" in self.headers:
            content_len = self.headers["Content-Length"]

        if content_len:
            return int(content_len)

    def get_redirect_url(self):
        if "Location" in self.headers and self.headers["Location"]:
            return self.headers["Location"]



class PageResponseObject(object):
    STATUS_CODE_OK = 200
    STATUS_CODE_ERROR = 500
    STATUS_CODE_UNDEF = 0

    def __init__(
        self,
        url=None,  # received url
        binary=None,
        text=None,
        status_code=STATUS_CODE_OK,
        encoding=None,
        headers=None,
        request_url=None,
    ):
        """
        @param contents Text

        TODO this should be cleaned up. We should pass binary, and encoding
        """
        self.errors = []
        self.url = url
        self.request_url = request_url
        self.status_code = status_code
        self.crawler_data = None
        self.crawl_time_s = None
        self.recognized_content_type = None
        self.body_hash = None
        self.is_allowed_internal = True

        if self.status_code is None:
            self.status_code = 0

        self.binary = None
        self.text = None

        if binary:
            self.binary = binary
        if text:
            self.text = text

        # I read selenium always assume utf8 encoding

        # encoding = chardet.detect(contents)['encoding']
        # self.apparent_encoding = encoding
        # self.encoding = encoding

        if not headers:
            self.headers = ResponseHeaders(headers={})
        else:
            self.headers = ResponseHeaders(headers=headers)

        headers_encoding = self.headers.get_encoding()
        if headers_encoding:
            self.encoding = headers_encoding
            self.apparent_encoding = headers_encoding
        elif encoding:
            self.encoding = encoding
            self.apparent_encoding = encoding
        else:
            self.encoding = "utf-8"
            self.apparent_encoding = "utf-8"

        if self.binary and not self.text:
            try:
                self.text = self.binary.decode(self.encoding)
            except Exception as E:
                WebLogger.exc(
                    E, "Cannot properly decode ansower from {}".format(self.url)
                )
                self.text = self.binary.decode(self.encoding, errors="ignore")

        if self.text and not self.binary:
            try:
                self.binary = self.text.encode(self.encoding)
            except Exception as E:
                WebLogger.exc(
                    E, "Cannot properly encode ansower from {}".format(self.url)
                )
                self.binary = self.text.encode(self.encoding, errors="ignore")

    def set_headers(self, headers):
        self.headers = ResponseHeaders(headers=headers)
        self.recognized_content_type = self.get_content_type()

    def set_recognized_content_type(self, recognized_type):
        self.recognized_content_type = recognized_type

    def get_recognized_content_type(self):
        if not self.recognized_content_type:
            self.recognized_content_type = self.headers.get_content_type()
            if self.recognized_content_type:
                wh = self.recognized_content_type.find(";")
                if wh >= 0:
                    self.recognized_content_type = self.recognized_content_type[:wh]

        return self.recognized_content_type

    def set_body_hash(self, body_hash):
        self.body_hash = body_hash

    def get_body_hash(self):
        return self.body_hash

    def set_crawler(self, crawler_data):
        self.crawler_data = dict(crawler_data)
        self.crawler_data["crawler"] = type(self.crawler_data["crawler"]).__name__

    def get_content_type(self):
        content_type = self.headers.get_content_type()
        if content_type is None:
            return self.recognized_content_type

        return content_type

    def get_content_type_keys(self):
        return self.headers.get_content_type_keys()

    def get_last_modified(self):
        return self.headers.get_last_modified()

    def is_content_html(self):
        content = self.headers.get_content_type()
        if not content:
            return False

        if content.lower().find("html") >= 0:
            return True

    def is_content_image(self):
        content = self.headers.get_content_type()
        if not content:
            return False

        if content.lower().find("image") >= 0:
            return True

    def is_content_rss(self):
        content = self.headers.get_content_type()
        if not content:
            return False

        if content.lower().find("rss") >= 0:
            return True
        if content.lower().find("xml") >= 0:
            return True

    def is_content_json(self):
        content = self.headers.get_content_type()
        if not content:
            return False

        if content.lower().find("json") >= 0:
            return True

    def get_content_length(self):
        length = self.headers.get_content_length()
        if length is not None:
            return length

        if self.text:
            return len(self.text)

        if self.binary:
            return len(self.binary)

        return 0

    def is_content_type_text(self):
        """
        You can preview on a browser headers. Ctr-shift-i on ff
        """
        content_type = self.get_content_type()
        if content_type.find("text") >= 0:
            return True
        if content_type.find("application") >= 0:
            return True
        if content_type.find("xml") >= 0:
            return True

        return False

    def get_redirect_url(self):
        return self.headers.get_redirect_url()

    def is_this_status_ok(self):
        if self.status_code is None:
            return False

        if self.status_code == HTTP_STATUS_UNKNOWN:
            return False

        # 300 are redirects - we don't know if these are valid

        return self.status_code >= 200 and self.status_code < 400

    def is_this_status_nok(self):
        """
        This function informs that status code is so bad, that further communication does not make any sense
        """
        if self.status_code is None:
            return True

        if self.status_code == HTTP_STATUS_UNKNOWN:
            # we do not know status of page yet
            return False

        if self.status_code == HTTP_STATUS_USER_AGENT:
            # if current agent is rejected, does not mean page (source) is invalid
            return False

        if self.status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
            # too many requests - we don't know what the page is
            return False

        if self.status_code == HTTP_STATUS_CODE_SERVER_ERROR:
            # server error - we don't know what the page is
            return False

        if self.status_code == HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS:
            # too many requests - we don't know what the page is
            return False

        if self.status_code < 200:
            return True

        if self.status_code >= 400:
            return True

    def is_this_status_redirect(self):
        """
        HTML code 403 - some pages block you because of your user agent. This code says exactly that.
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        """
        return (
            self.status_code > 300 and self.status_code < 400
        ) or self.status_code == 403

    def is_valid(self):
        # TODO this needs to check if it is 200 and 400
        if self.is_this_status_ok():
            return True

        return False

    def is_invalid(self):
        if self.is_this_status_nok():
            return True

        return False

    def is_allowed(self):
        return self.is_allowed_internal

    def get_status_code(self):
        return self.status_code

    def get_text(self):
        return self.text

    def get_binary(self):
        return self.binary

    def get_streams(self):
        if self.text is not None:
            return [self.text]
        elif self.binary:
            return [self.binary]

        return []

    def get_headers(self):
        clean_headers = self.headers.get_clean_headers()
        content_type = self.headers.get_content_type()
        if content_type is None:
            if self.recognized_content_type:
                clean_headers["Content-Type"] = self.recognized_content_type

        return clean_headers

    def set_text(self, text, encoding=None):
        if encoding:
            self.encoding = encoding
        else:
            if self.encoding is None:
                self.encoding = "utf-8"

        self.text = text
        self.binary = text.encode(self.encoding)

    def set_binary(self, binary, encoding="utf-8"):
        self.binary = binary
        self.text = binary.decode(encoding)

    def add_error(self, error_text):
        self.errors.append(error_text)

    def __str__(self):
        has_text_data = "Yes" if self.text else "No"
        has_binary_data = "Yes" if self.binary else "No"

        status_code_text = status_code_to_text(self.status_code)

        return "PageResponseObject: Url:{} Status code:{} Headers:{} Text:{} Binary:{}".format(
            self.url,
            status_code_text,
            self.headers,
            has_text_data,
            has_binary_data,
        )

    def is_html(self):
        if self.get_content_type() is not None and self.is_content_html():
            return True

    def is_rss(self):
        if self.get_content_type() is not None and self.is_content_rss():
            return True

    def is_json(self):
        if self.get_content_type() is not None and self.is_content_json():
            return True

    def is_text(self):
        if (
            self.get_content_type() is not None
            and self.get_content_type().find("text") >= 0
        ):
            return True

    def is_content_type(self, inner):
        if (
            self.get_content_type() is not None
            and self.get_content_type().find(inner) >= 0
        ):
            return True

    def get_encoding(self):
        return self.encoding

    def get_hash(self):
        text = self.get_text()
        if text:
            return calculate_hash(text)

        binary = self.get_binary()
        if binary:
            return calculate_hash_binary(binary)


def get_response_to_bytes(response):
    from .ipc import string_to_command

    total_bytes = bytearray()

    bytes1 = string_to_command("PageResponseObject.__init__", "OK")
    bytes2 = string_to_command("PageResponseObject.url", response.url)
    bytes3 = string_to_command(
        "PageResponseObject.status_code", str(response.status_code)
    )
    if response.headers != None:
        bytes4 = string_to_command(
            "PageResponseObject.headers", json.dumps(response.headers)
        )
    else:
        bytes4 = bytearray()

    if response.text:
        bytes5 = string_to_command("PageResponseObject.text", response.text)
    elif response.binary:
        bytes5 = bytes_to_command("PageResponseObject.text", response.binary)
    else:
        bytes5 = bytearray()
    bytes6 = string_to_command(
        "PageResponseObject.request_url", str(response.request_url)
    )
    bytes7 = string_to_command("PageResponseObject.__del__", "OK")

    total_bytes.extend(bytes1)
    total_bytes.extend(bytes2)
    total_bytes.extend(bytes3)
    total_bytes.extend(bytes4)
    total_bytes.extend(bytes5)
    total_bytes.extend(bytes6)
    total_bytes.extend(bytes7)

    return total_bytes


def get_response_from_bytes(all_bytes):
    from .ipc import commands_from_bytes

    response = PageResponseObject("")

    commands_data = commands_from_bytes(all_bytes)
    for command_data in commands_data:
        if command_data[0] == "PageResponseObject.__init__":
            pass
        elif command_data[0] == "PageResponseObject.url":
            response.url = command_data[1].decode()
        elif command_data[0] == "PageResponseObject.request_url":
            response.request_url = command_data[1].decode()
        elif command_data[0] == "PageResponseObject.headers":
            try:
                response.headers = json.loads(command_data[1].decode())
            except ValueError as E:
                WebLogger.exc(E, "Exception when loading headers")
        elif command_data[0] == "PageResponseObject.status_code":
            try:
                response.status_code = int(command_data[1])
            except ValueError as E:
                WebLogger.exc(E, "Exception when loading headers")
        elif command_data[0] == "PageResponseObject.text":
            response.set_text(command_data[1].decode())
        elif command_data[0] == "PageResponseObject.__del__":
            pass

    return response


def response_to_json(response, with_streams=False):
    """
    """
    response_data = OrderedDict()

    if response:
        response_data["url"] = response.url
        response_data["request_url"] = response.request_url
        response_data["headers"] = response.get_headers()

        response_data["is_valid"] = response.is_valid()
        response_data["is_invalid"] = response.is_invalid()
        response_data["is_allowed"] = response.is_allowed()

        response_data["status_code"] = response.get_status_code()
        response_data["status_code_str"] = status_code_to_text(
            response.get_status_code()
        )

        response_data["crawl_time_s"] = response.crawl_time_s
        response_data["Content-Type"] = response.get_content_type()
        response_data["Recognized-Content-Type"] = response.get_recognized_content_type()
        response_data["Content-Length"] = response.get_content_length()
        response_data["Last-Modified"] = response.get_last_modified()
        response_data["Charset"] = response.get_encoding()
        contents_hash = response.get_hash()
        if contents_hash:
            response_data["hash"] = json_encode_field(contents_hash)
        else:
            response_data["hash"] = None
        body_hash = response.get_body_hash()
        if body_hash:
            response_data["body_hash"] = json_encode_field(body_hash)
        else:
            response_data["body_hash"] = None

        if len(response.errors) > 0:
            response_data["errors"] = []
            for error in response.errors:
                response_data["errors"].append(error)

        if with_streams:
            response_data["streams"] = response.get_streams()
            response_data["text"] = response.get_text()
            response_data["binary"] = json_encode_field(response.get_binary())
    else:
        response_data["is_valid"] = False
        response_data["status_code"] = HTTP_STATUS_CODE_EXCEPTION
        response_data["status_code_str"] = status_code_to_text(HTTP_STATUS_CODE_EXCEPTION)

    return response_data


def json_to_response(json_data, with_streams=False):
    url = json_data.get("url")
    request_url = json_data.get("request_url")
    streams = json_data.get("streams")
    text = json_data.get("text")
    binary = json_data.get("binary")
    status_code = json_data.get("status_code")
    encoding = json_data.get("Charset")
    headers = json_data.get("headers")
    body_hash = json_data.get("body_hash")

    if binary:
        binary = base64.b64decode(binary)
    if body_hash:
        body_hash = base64.b64decode(body_hash)

    response = PageResponseObject(
        url=url,  # received url
        binary=binary,
        text=text,
        status_code=status_code,
        encoding=encoding,
        headers=headers,
        request_url=request_url,
    )

    response.body_hash = body_hash

    return response


def response_to_file(response, file_name):
    if not response:
        return

    with open(file_name, "w") as fh:
        json_data = response_to_json(response)
        json_text = json.dumps(json_data)
        
        fh.write(json_text)


def file_to_response(file_name):
    with open(file_name, "r") as fh:
        json_text = fh.read()
        json_data = json.loads(json_text)

        return json_to_response(json_data)
