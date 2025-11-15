from .contentinterface import ContentInterface
from .remoteserver import RemoteServer
from .webtools import json_decode_field


class RemoteUrl(ContentInterface):
    def __init__(
        self,
        url=None,
        remote_server_location=None,
        all_properties=None,
        social_properties=None,
    ):
        super().__init__(url=url, contents=None)
        self.remote_server_location = remote_server_location
        self.server = RemoteServer(remote_server_location)

        self.all_properties = all_properties
        self.social_properties = social_properties

        self.responses = None
        if self.all_properties:
            self.get_responses()

    def get_responses(self):
        if self.all_properties is None:
            self.all_properties = self.server.get_getj(url=self.url)

        if not self.responses:
            self.responses = {"Default": RemoteServer.get_response(self.all_properties)}

        return self.responses

    def get_response(self):
        if "Default" in self.get_responses():
            return self.responses["Default"]

    def get_text(self):
        responses = self.get_responses()
        if "Text" in responses:
            return responses["Text"].get_text()
        if "Default" in responses:
            return responses["Default"].get_text()

    def get_binary(self):
        responses = self.get_responses()
        if "Binary" in responses:
            return responses["Binary"].get_text()
        if "Default" in responses:
            return responses["Default"].get_binary()

    def get_properties(self):
        if self.all_properties is None:
            self.get_responses()
            if self.all_properties is None:
                return {}

        properties = RemoteServer.read_properties_section(
            "Properties", self.all_properties
        )
        return properties

    def get_canonical_link(self):
        if "link_canonical" in self.get_properties():
            return properties["link_canonical"]

    def is_valid(self):
        response = self.get_response()
        if not response:
            return False

        return response.is_valid()

    def is_invalid(self):
        response = self.get_response()
        if not response:
            return False

        return response.is_invalid()

    def get_title(self):
        return self.get_properties().get("title")

    def get_description(self):
        return self.get_properties().get("description")

    def get_language(self):
        return self.get_properties().get("language")

    def get_thumbnail(self):
        return self.get_properties().get("thumbnail")

    def get_author(self):
        return self.get_properties().get("author")

    def get_album(self):
        return self.get_properties().get("album")

    def get_tags(self):
        return self.get_properties().get("tags")

    def get_date_published(self):
        return self.get_properties().get("date_published")  # TODO parse?

    def get_status_code(self):
        return self.get_response().status_code

    def get_entries(self):
        entries = RemoteServer.read_properties_section("Entries", self.all_properties)
        if entries:
            return entries
        return []

    def get_feeds(self):
        """
        Can be called to obtain calculated "easy feeds", or fetch contents, and return
        feeds based also on the contents.
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

        return feeds

    def get_links(self):
        return self.server.get_linkj(self.url)

    def get_hash(self):
        return self.get_response().get_hash()

    def get_body_hash(self):
        return self.get_response().get_body_hash()

    def get_meta_hash(self):
        hash_section = RemoteServer.read_properties_section(
            "PropertiesHash", self.all_properties
        )
        if hash_section:
            return json_decode_field(hash_section)

    def get_social_properties(self):
        if self.social_properties is None:
            self.social_properties = self.server.get_socialj(self.url)

        return self.social_properties
