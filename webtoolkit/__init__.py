"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webtools import *
from .statuses import *
from .webconfig import WebConfig
from .response import *
from .request import *

from .contentinterface import ContentInterface
from .contentlinkparser import ContentLinkParser
from .contenttext import ContentText
from .urllocation import UrlLocation
from .remoteserver import RemoteServer
from .remoteurl import RemoteUrl

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

from .crawlers import *
from .handlers import *

from .baseurl import BaseUrl
from .domaincache import *
