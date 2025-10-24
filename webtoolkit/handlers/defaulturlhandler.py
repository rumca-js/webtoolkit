import copy

from ..utils.dateutils import DateUtils
from ..pages import DefaultContentPage
from ..request import PageRequestObject
from .handlerhttppage import HttpPageHandler


class DefaultUrlHandler(HttpPageHandler):
    """
    """

    def __init__(self, url=None, contents=None, settings=None, request=None, url_builder=None):
        super().__init__(url, settings=settings, request=request, url_builder=url_builder)
        self.code = self.input2code(url)

    def get_page_url(self, url, crawler_name=None):
        """
        Obtains a custom, another URL using a crawler
        Necessary for more advanced handlers that in order to provide necessary data
        check multiple source of data.
        """
        if self.request:
            request = copy.copy(self.request)
        else:
            request = PageRequestObject(url)

        request.url = url
        request.handler_type = HttpPageHandler

        if crawler_name:
            request.crawler_name = crawler_name

        if self.url_builder:
            url = self.url_builder(url=url, request=request)
            return url


class DefaultChannelHandler(DefaultUrlHandler):
    """
    Default handler for channels
    """
    pass
