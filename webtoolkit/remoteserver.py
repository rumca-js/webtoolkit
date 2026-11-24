from collections import OrderedDict
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
    response_to_json,
)


class RemoteServer(object):
    """
    Crawler buddy communication class
    """

    def __init__(self, remote_server=None, timeout_s=30, client_id=None, key=None):
        self.remote_server = remote_server
        if not self.remote_server:
            self.remote_server = RemoteServer.get_remote_server_location()

        self.timeout_s = timeout_s
        self.client_id = client_id
        self.key = key

    def get_remote_server_location():
        CRAWLER_BUDDY_SERVER = os.environ.get("CRAWLER_BUDDY_SERVER")
        CRAWLER_BUDDY_PORT = os.environ.get("CRAWLER_BUDDY_PORT")
        if CRAWLER_BUDDY_SERVER and CRAWLER_BUDDY_PORT:
            return f"http://{CRAWLER_BUDDY_SERVER}:{CRAWLER_BUDDY_PORT}"

    def _call_url_endpoint(self, endpoint, request=None, url=None):
        if url and not request:
            request = PageRequestObject(url)
            request.url = url.strip()

        if not request or not request.url:
            return None

        link = f"{self.remote_server}{endpoint}"
        return self.perform_remote_call(link_call=link, request=request)

    def _call_global_endpoint(self, endpoint, timeout_s=10):
        if not self.remote_server:
            return None

        link = f"{self.remote_server}{endpoint}"
        try:
            with requests.get(url=link, timeout=timeout_s, verify=False) as result:
                if result.status_code == 200 and result.text:
                    return json.loads(result.text)
                return None
        except Exception:
            return None

    def get_page_data(self, request=None, url=None):
        """Maps to /api/get"""
        return self._call_url_endpoint("/api/get", request=request, url=url)

    def get_getj(self, request=None, url=None):
        return self.get_page_data(request=request, url=url)

    def get_head_data(self, request=None, url=None):
        """Maps to /api/head"""
        return self._call_url_endpoint("/api/head", request=request, url=url)

    def get_feeds(self, request=None, url=None):
        """Maps to /api/feeds"""
        return self._call_url_endpoint("/api/feeds", request=request, url=url)

    def get_feedsj(self, request=None, url=None):
        return self.get_feeds(request=request, url=url)

    def get_social(self, request=None, url=None):
        """Maps to /api/social"""
        return self._call_url_endpoint("/api/social", request=request, url=url)

    def get_socialj(self, request=None, url=None):
        return self.get_social(request=request, url=url)

    def get_link(self, request=None, url=None):
        """Maps to /api/link"""
        return self._call_url_endpoint("/api/link", request=request, url=url)

    def get_linkj(self, request=None, url=None):
        return self.get_link(request=request, url=url)

    def get_scan_links(self, request=None, url=None):
        """Maps to /api/scanlinks"""
        return self._call_url_endpoint("/api/scanlinks", request=request, url=url)

    def get_scanlinks(self, request=None, url=None):
        return self.get_scan_links(request=request, url=url)

    def get_scan_domains(self, request=None, url=None):
        """Maps to /api/scandomains"""
        return self._call_url_endpoint("/api/scandomains", request=request, url=url)

    def get_archives(self, request=None, url=None):
        """Maps to /api/archives"""
        return self._call_url_endpoint("/api/archives", request=request, url=url)

    def get_find(self, request=None, url=None):
        """Maps to /api/find"""
        return self._call_url_endpoint("/api/find", request=request, url=url)

    def remove_history_entry(self, request=None, url=None):
        """Maps to /api/remove"""
        return self._call_url_endpoint("/api/remove", request=request, url=url)

    def get_ping(self, request=None, url=None):
        """Maps to /api/ping"""
        json_obj = self._call_url_endpoint("/api/ping", request=request, url=url)
        if isinstance(json_obj, dict):
            return json_obj.get("status")
        return json_obj

    def get_pingj(self, request=None, url=None):
        return self.get_ping(request=request, url=url)

    def get_info(self):
        """Maps to /api/info"""
        return self._call_global_endpoint("/api/info")

    def get_infoj(self):
        return self.get_info()

    def get_history(self):
        """Maps to /api/history"""
        return self._call_global_endpoint("/api/history")

    def clear_history(self):
        """Maps to /api/clear"""
        return self._call_global_endpoint("/api/clear")

    def perform_remote_call_with_retry(self, link_call, request):
        """
        This function may make the call several times (in case server is busy).
        This could be dangerous, so not doing it right now
        """

        return self.perform_remote_call(link_call, request)

    def perform_remote_call(self, link_call, request):
        """
        @param link_call Remote server endpoint
        @param url Url for which we call Remote server

        Note: there should always be a timeout. Server might stop responding,
        it could have hanged, etc.
        """
        url = request.url

        encoded_request = request_encode(request)

        if self.key:
            encoded_request = encoded_request + "&key="+self.key
        if self.client_id:
            encoded_request = encoded_request + "&client_id="+self.client_id

        link_call = f"{link_call}?{encoded_request}"

        text = None

        # it is hard to think of a good deafult value
        timeout_s = 60
        if request.timeout_s is not None:
            # remote server will have timeout_s we add some wiggle room for transmission
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

        if json_obj and "success" in json_obj and not json_obj["success"]:
            print("Url:{} Remote error. Not a success".format(link_call))
            return
        return json_obj

    def is_remote_server_ok(link_call):
        try:
            with requests.get(url=link_call, timeout=timeout_s, verify=False) as result:
                return result.status_code == 200
        except Exception as E:
            return False

    def get_properties(self, url=None, request=None):
        json_obj = self.get_page_data(url=url, request=request)

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

    def get_responses(all_properties):
        if not all_properties:
            return

        responses = OrderedDict()

        streams_data = RemoteServer.read_properties_section("Streams", all_properties)
        if streams_data and len(streams_data) > 0:
            for item in streams_data:
                response_data = streams_data[item]
                response = json_to_response(response_data)
                if response.url:
                    responses[item] = response

        return responses

    def get_response(all_properties):
        """
        Returns response from all properties
        """

        """
        responses = RemoteServer.get_responses(all_properties)
        if not responses:
            return

        if "Default" in responses:
            return responses["Default"]

        # first try to return stream that matches request link
        properties = RemoteServer.read_properties_section("Properties", all_properties)
        if properties:
            link = properties.get("link")
            if link:
                response = responses.get(link)
                if response:
                    return response

        # return first found response
        for url in responses:
            return responses[url]
        """

        response_data = RemoteServer.read_properties_section("Response", all_properties)
        response = json_to_response(response_data)
        return response

    def encode(data):
        return urllib.parse.quote(data, safe="")

    def get_infoj(self):
        link = self.remote_server
        link = f"{link}/api/info"

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

    def set(self, response, crawl_id=None, url=None, crawler_name=None, handler_name=None):
        """
        args - params
        """
        timeout_s = 60
        remote_server = self.remote_server

        response_json = response_to_json(response)

        params = {}
        if url:
            params["url"] = url
        if crawl_id:
            params["crawl_id"] = crawl_id
        if crawler_name:
            params["crawler_name"] = crawler_name
        if handler_name:
            params["handler_name"] = handler_name

        link_call = f"{remote_server}/set"
        try:
            r = requests.post(url=link_call,
                          timeout=timeout_s,
                          verify=False,
                          json=response_json,
                          params=params)
            r.close()

            if r.status_code == 200:
                return True

            #r.raise_for_status()

        except requests.RequestException as E:
            print("Cannot post request")
            #print(str(response_json))

    def findj(self, crawl_id=None, url=None, crawler_name=None, handler_name=None):
        timeout_s = 60
        remote_server = self.remote_server

        link_call = f"{remote_server}/findj"

        params = {}
        if url:
            params["url"] = url
        if crawl_id:
            params["crawl_id"] = crawl_id
        if crawler_name:
            params["crawler_name"] = crawler_name
        if handler_name:
            params["handler_name"] = handler_name

        with requests.get(link_call, params=params) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except Exception as E:
                    print("Response content is not valid JSON. {}".format(E))
