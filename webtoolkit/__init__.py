"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webtools import *
from .webconfig import WebConfig

from .contentinterface import ContentInterface
from .contentlinkparser import ContentLinkParser
from .urllocation import UrlLocation
from .remoteserver import RemoteServer

from .pages import (
   DefaultContentPage,
   HtmlPage,
   RssPage,
   RssContentReader,
   OpmlPage,
   JsonPage,
   PageFactory,
)

from .contentmoderation import (
    UrlPropertyValidator,
    UrlPropertyValidator,
    UrlAgeModerator,
)
