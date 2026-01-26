"""
Remote URL provides capabilities to call a network crawling server and read responses.
This class acts as a client to a remote server that performs the actual crawling,
allowing for the separation of crawling logic from the application.

@example
url = RemoteUrl("https://127.0.0.1:8080")
response = url.get_response()
print(response.status_code)
"""

from collections import OrderedDict
from typing import Any, Dict, List, Optional, Set

from .contentinterface import ContentInterface
from .remoteserver import RemoteServer
from .request import PageRequestObject
from .response import PageResponseObject
from .webtools import json_decode_field


class RemoteUrl(ContentInterface):
    """
    Represents a URL to be processed by a remote network crawler.
    This class can either fetch data from a remote server or operate on data that has already been fetched.
    """

    def __init__(
        self,
        url=None,
        request=None,
        remote_server_location=None,
        all_properties=None,
        social_properties=None,
    ):
        """
        Initializes the RemoteUrl object.
        :param url: The URL to be processed.
        :param request: A PageRequestObject for the URL.
        :param remote_server_location: The location of the remote crawling server.
        :param all_properties: A dictionary of pre-fetched properties for the URL.
        :param social_properties: A dictionary of pre-fetched social media properties.
        """
        super().__init__(url=url, contents=None)
        self.request = request
        self.remote_server_location = remote_server_location
        self.server = RemoteServer(remote_server_location)
        self.all_properties = all_properties
        self.social_properties = social_properties

        self.responses = None
        if self.all_properties:
            self.get_responses()

    def get_responses(self):
        """Provides URL responses"""
        if self.all_properties is None:
            self.all_properties = self.server.get_getj(
                url=self.url, request=self.request
            )

        if not self.responses and self.all_properties:
            self.responses = RemoteServer.get_responses(self.all_properties)

        return self.responses

    def get_response(self):
        """Provides URL response"""
        responses = self.get_responses()
        if not responses:
            return

        if "Default" in responses:
            return responses["Default"]
        for url in responses:
            return responses[url]

    def get_text(self):
        """Provides URL response text. Useful if link provides one response."""
        response = self.get_response()
        if response and response.get_text():
            return response.get_text()

    def get_binary(self):
        """Provides URL response binary"""
        response = self.get_response()
        if response and respose.get_binary():
            return response.get_binary()

    def get_properties(self):
        """
        Retrieves the basic properties of the URL.
        :return: A dictionary of properties.
        """
        if self.all_properties is None:
            self.get_responses()
            if self.all_properties is None:
                return {}

        properties = RemoteServer.read_properties_section(
            "Properties", self.all_properties
        )
        return properties

    def get_all_properties(self):
        """
        Retrieves all properties of the URL.
        :return: A dictionary of all properties.
        """
        return self.all_properties

    def get_canonical_link(self):
        """Returns URL canonical link."""

        return self.get_properties().get("link_canonical")

    def is_valid(self):
        """Returns true if URL data is valid"""
        response = self.get_response()
        if not response:
            return False

        return response.is_valid()

    def is_invalid(self) -> bool:
        """Returns true if URL data is invalid"""
        response = self.get_response()
        if not response:
            return False

        return response.is_invalid()

    def get_title(self):
        """Returns title"""
        return self.get_properties().get("title")

    def get_description(self):
        """Returns description"""
        return self.get_properties().get("description")

    def get_language(self):
        """Returns language"""
        return self.get_properties().get("language")

    def get_thumbnail(self):
        """Returns thumbnail"""
        return self.get_properties().get("thumbnail")

    def get_author(self):
        """Returns author"""
        return self.get_properties().get("author")

    def get_album(self):
        """Returns album"""
        return self.get_properties().get("album")

    def get_tags(self):
        """Returns tags. TODO return value?"""
        return self.get_properties().get("tags")

    def get_date_published(self):
        """Returns date published. TODO - should be a date"""
        return self.get_properties().get("date_published")  # TODO parse?

    def get_status_code(self):
        """Returns status code"""
        response = self.get_response()
        if response:
            return response.status_code

    def get_entries(self):
        """
        Retrieves the entries from the URL's properties.
        :return: A list of entries, or an empty list if not available.
        """
        entries = RemoteServer.read_properties_section("Entries", self.all_properties)
        if entries:
            return entries
        return []

    def get_feeds(self):
        """
        Retrieves the feeds associated with the URL.
        :return: A set of feed URLs.
        """
        if self.all_properties is not None:
            feeds = self.get_properties().get("feeds")
        else:
            feeds_json = self.server.get_feedsj(url=self.url)
            if not feeds_json:
                return set()
            feeds = feeds_json.get("feeds")

        if feeds is None:
            return set()

        return set(feeds)

    def get_links(self):
        """
        Retrieves information about links (canonical, archive, etc.) for the URL.
        :return: A dictionary of link information.
        """
        return self.server.get_linkj(self.url)

    def get_hash(self):
        """
        Retrieves the hash of the response.
        :return: The hash of the response, or None if not available.
        """
        response = self.get_response()
        if response:
            return response.get_hash()

    def get_body_hash(self):
        """
        Retrieves the body hash of the response.
        :return: The body hash, or None if not available.
        """
        response = self.get_response()
        if response:
            return response.get_body_hash()

    def get_meta_hash(self):
        """
        Retrieves the meta hash from the URL's properties.
        :return: The decoded meta hash, or None if not available.
        """
        hash_section = RemoteServer.read_properties_section(
            "PropertiesHash", self.all_properties
        )
        if hash_section:
            return json_decode_field(hash_section)

    def get_social_properties(self):
        """
        Retrieves social media properties for the URL.
        :return: A dictionary of social media properties.
        """
        if self.social_properties is None:
            self.social_properties = self.server.get_socialj(
                url=self.url, request=self.request
            )
        return self.social_properties
