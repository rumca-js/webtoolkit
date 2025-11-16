import json
import requests
import urllib.parse
import os

from .statuses import (
    HTTP_STATUS_TOO_MANY_REQUESTS,
)
from .request import (
    request_encode,
    PageRequestObject,
)
from .response import (
    PageResponseObject,
    json_to_response,
)


class RemoteServer(object):
    """
    Crawler buddy communication class
    """

    def __init__(self, remote_server=None, timeout_s=30):
        self.remote_server = remote_server
        if not self.remote_server:
            CRAWLER_BUDDY_SERVER = os.environ.get("CRAWLER_BUDDY_SERVER")
            CRAWLER_BUDDY_PORT = os.environ.get("CRAWLER_BUDDY_PORT")
            if CRAWLER_BUDDY_SERVER and CRAWLER_BUDDY_PORT:
                self.remote_server = (
                    f"http://{CRAWLER_BUDDY_SERVER}:{CRAWLER_BUDDY_PORT}"
                )

        self.timeout_s = timeout_s

    def get_getj(self, request=None, url=None):
        """
        @returns None in case of error
        """
        if url and not request:
            request = PageRequestObject(url)
            request.url = url
            request.url = request.url.strip()

        if not request or not request.url:
            return

        link = self.remote_server
        link = f"{link}/getj"

        return self.perform_remote_call(link_call=link, request=request)

    def get_feedsj(self, request=None, url=None):
        """
        @returns None in case of error
        """

        if url and not request:
            request = PageRequestObject(url)
            request.url = url
            request.url = request.url.strip()

        if not request or not request.url:
            return

        link = self.remote_server
        link = f"{link}/feedsj"

        return self.perform_remote_call(link, request)

    def get_socialj(self, request=None, url=None):
        """
        @returns None in case of error
        """

        if url and not request:
            request = PageRequestObject(url)
            request.url = url
            request.url = request.url.strip()

        if not request or not request.url:
            return

        link = self.remote_server
        link = f"{link}/socialj"

        return self.perform_remote_call(link, request)

    def get_linkj(self, request=None, url=None):
        """
        @returns None in case of error
        """
        if url and not request:
            request = PageRequestObject(url)
            request.url = url
            request.url = request.url.strip()

        if not request or not request.url:
            return

        link = self.remote_server
        link = f"{link}/linkj"

        return self.perform_remote_call(link, request)

    def get_pingj(self, request=None, url=None):
        """
        @returns None in case of error
        """
        if url and not request:
            request = PageRequestObject(url)
            request.url = url
            request.url = request.url.strip()

        if not request or not request.url:
            return

        link = self.remote_server
        link = f"{link}/pingj"

        json = self.perform_remote_call(link, request)
        if json:
            return json.get("status")

    def perform_remote_call(self, link_call, request):
        """
        @param link_call Remote server endpoint
        @param url Url for which we call Remote server
        """
        url = request.url

        encoded_request = request_encode(request)

        link_call = f"{link_call}?{encoded_request}"

        text = None

        timeout_s = 50
        if request.timeout_s is not None:
            timeout_s = request.timeout_s
            timeout_s += 5

        print(f"Remote server: Calling {link_call}")

        try:
            with requests.get(url=link_call, timeout=timeout_s, verify=False) as result:
                text = result.text
        except Exception as E:
            print("Remote error. " + str(E))
            return

        if not text:
            print("Remote error. No text")
            return

        # print("Calling:{}".format(link))

        json_obj = None
        try:
            json_obj = json.loads(text)
        except ValueError as E:
            print(
                "Url:{} Remote error. Value error in response".format(link_call, text)
            )
            print(str(E))
            return
        except TypeError as E:
            print("Url:{} Remote error. Type error response".format(link_call, text))
            print(str(E))
            return

        if "success" in json_obj and not json_obj["success"]:
            print("Url:{} Remote error. Not a success".format(link_call))
            return

        return json_obj

    def get_properties(self, url=None, request=None):
        json_obj = self.get_getj(url=url, request=request)

        if json_obj:
            return RemoteServer.read_properties_section("Properties", json_obj)

        return json_obj

    def read_properties_section(section_name, all_properties):
        if not all_properties:
            return

        if "success" in all_properties and not all_properties["success"]:
            # print("Url:{} Remote error. Not a success".format(link))
            print("Remote error. Not a success")
            return False

        for properties in all_properties:
            if section_name == properties["name"]:
                return properties["data"]

    def unpack_data(self, input_data):
        """
        TODO remove?
        """
        json_data = {}

        data = json.loads(input_data)

        response = RemoteServer.read_properties_section("Response", data)
        contents_data = RemoteServer.read_properties_section("Contents", data)

        if response:
            json_data["status_code"] = response["status_code"]
        if contents_data:
            json_data["contents"] = contents_data["Contents"]
        if response:
            json_data["Content-Length"] = response["Content-Length"]
        if response:
            json_data["Content-Type"] = response["Content-Type"]

        return json_data

    def get_response(all_properties):
        if not all_properties:
            return

        response_data = RemoteServer.read_properties_section("Response", all_properties)
        if not response_data:
            return

        response = json_to_response(response_data)
        if not response:
            return

        streams = RemoteServer.read_properties_section("Streams", all_properties)

        if streams and "Text" in streams:
            response.text = streams["Text"]

        if streams and "Binary" in streams:
            response.binary = streams["Binary"]

        if not response.text and streams and len(streams) > 0:
            for item in streams:
                response = json_to_response(streams[item])
                return response

        return response

    def encode(data):
        return urllib.parse.quote(data, safe="")

    def get_infoj(self):
        link = self.remote_server
        link = f"{link}/infoj"

        timeout_s = 10

        try:
            with requests.get(url=link, timeout=timeout_s, verify=False) as result:
                text = result.text
        except Exception as E:
            print("Remote error. " + str(E))
            return

        if not text:
            print("Remote error. No text")
            return

        # print("Calling:{}".format(link))

        json_obj = None
        try:
            json_obj = json.loads(text)
            return json_obj
        except ValueError as E:
            print(
                "Url:{} Remote error. Value error in response".format(link_call, text)
            )
            print(str(E))
            return
        except TypeError as E:
            print("Url:{} Remote error. Type error response".format(link_call, text))
            print(str(E))
            return
