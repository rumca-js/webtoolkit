"""
Defines UrlInterface extending ContentInterface.
"""

from .contentinterface import ContentInterface
from .response import PageResponseObject


class UrlInterface(ContentInterface):
    """
    Interface for URL objects (BaseUrl, RemoteUrl) that manage and expose raw HTTP responses.
    """

    def get_response(self) -> PageResponseObject | None:
        """
        Returns primary stream response object or None.
        """
        return None

    def get_general_response(self) -> PageResponseObject | None:
        """
        Returns primary stream response object if all streams succeeded,
        PageResponseObject with status_code=0 if any stream failed,
        or None if no streams are present.
        """
        return None
