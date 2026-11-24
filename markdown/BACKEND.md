# Backend Architecture

## Entry Points

BaseUrl (webtoolkit/baseurl.py)
  - Main user-facing class. Accepts a URL string, dispatches to handlers and crawlers,
    caches responses, and exposes ContentInterface getters.
  - Key methods: get_response(), get_title(), get_description(), get_date_published(),
    get_author(), get_feeds(), get_entries(), get_links(), get_social_data(),
    get_social_properties(), is_alive(), close()
  - Context manager: implements __enter__ and __exit__, ensuring deterministic disposal.

### Lifecycle & Disposal

BaseUrl instances are designed for single URL usage, fetched once, and disposed cleanly:
- **State Machine**:
  - `INIT`: `BaseUrl(url=...)` created. `self._closed = False`, `self.handler = None`.
  - `ACTIVE`: `get_response()` or content getter invoked. Handler is created, response is fetched. Subsequent calls delegate to handler.
  - `CLOSED`: `close()` or context manager exit (`__exit__`). `self._closed = True`, fetch artifacts (`handler`, `request`) are nulled.
  - Attempting to call `get_response()` or `get_general_response()` (or dependent getters like `get_contents()`, `get_binary()`, `get_meta_hash()`, `get_all_properties()`, `get_response_data()`) while in the `CLOSED` state raises `RuntimeError("BaseUrl is closed")`.
- **Disposal Chain**:
  - `BaseUrl.close()`: Sets `self._closed = True`, tears down crawler references in stream requests, calls `self.handler.close()`, and nulls `self.handler`, `self.request`.
  - `HandlerInterface.close()`: Sets `self.request = None`, `self.streams = {}`.
  - `HttpPageHandler.close()`: Calls `super().close()` and additionally sets `self.p = None` (clearing parsed page objects like `HtmlPage`, `RssPage`).
  - `close()` is idempotent: multiple invocations do not raise.

RemoteUrl (webtoolkit/remoteurl.py)
  - Drop-in alternative to BaseUrl for delegating crawling and parsing to a remote
    crawler-buddy service. Exposes the same ContentInterface API, including
    get_social_data() and get_social_properties() returning SocialData instances.

## Handler Layer (webtoolkit/handlers/)

HandlerInterface (handlerinterface.py)
  - Abstract base for all handlers. Extends DefaultContentPage. Holds response, streams
    container map (`dict[str, PageResponseObject]`), and url_builder.
  - Implements container-backed `get_response()` (returns primary response), `get_responses()` (returns all streams),
    and `get_streams()` (serialized JSON map). Subclasses override is_handled_by(), input2code(), code2url().
  - Platform handlers fetch auxiliary endpoints into `streams` via `build_http_url()`, preserving downstream custom crawlers.

DefaultUrlHandler (defaulturlhandler.py)
  - Fallback handler for plain HTTP URLs. Delegates to HttpPageHandler.

DefaultChannelHandler (defaulturlhandler.py)
  - Base for channel/feed-style handlers (YouTube channel, Odysee channel, etc.).

HttpPageHandler (handlerhttppage.py)
  - Core handler: fires the crawler, receives PageResponseObject, passes it through
    PageFactory to produce a typed Page object (HtmlPage, RssPage, etc.).

Platform handlers:
  - RedditUrlHandler (handlers.py) — Reddit post and subreddit JSON API
  - HandlerChannelYoutube (handlerchannelyoutube.py) — YouTube channel metadata/feeds
  - HandlerVideoYoutube (handlervideoyoutube.py) — YouTube video metadata via yt-dlp
  - HandlerChannelOdysee (handlerchannelodysee.py) — Odysee channel
  - HandlerVideoOdysee (handlervideoodysee.py) — Odysee video

## Crawler Layer (webtoolkit/crawlers/)

CrawlerInterface (crawlerinterface.py)
  - Abstract transport interface. Implementations receive a PageRequestObject and return
    a PageResponseObject.

RequestsCrawler (requestscrawler.py)
  - Default HTTP transport using the requests library. Handles headers, user-agents,
    timeouts, and status codes.

## Page / Content Layer (webtoolkit/pages.py)

PageFactory
  - Inspects Content-Type and raw content to instantiate the correct page type.

Page types (all implement ContentInterface):
  - HtmlPage — HTML document parsing via BeautifulSoup/lxml
  - RssPage / RssContentReader — RSS/Atom feed parsing via brutefeedparser
  - OpmlPage — OPML subscription list
  - JsonPage — Generic JSON response
  - XmlPage — Generic XML
  - DefaultContentPage — Fallback / base implementation

## Social Data Layer (webtoolkit/socialdata.py)

SocialData & SocialSourceResult:
  - `SocialData`: Dataclass containing social engagement metrics (`thumbs_up`, `thumbs_down`,
    `view_count`, `rating`, `upvote_ratio`, `upvote_diff`, `upvote_view_ratio`, `stars`,
    `followers_count`), `errors: list[str] | None`, and `sources: list[SocialSourceResult]`.
  - `SocialSourceResult`: Per-source tracking dataclass (`name`, `ok`, `error`).
  - Handlers (`HandlerVideoYoutube`, `RedditUrlHandler`, `GitHubUrlHandler`, `HackerNewsHandler`,
    `ReturnDislike`) fetch auxiliary API responses into `streams` via `build_http_url()` and implement
    `get_social_data() -> SocialData` with granular per-source error reporting and logging.
  - `SocialData.set_sources(sources)` helper populates `sources` and extracts non-empty error strings into `errors`.
  - `SocialData.from_dict(data)` deserializes raw JSON/dict responses, extracting engagement metrics, nested sources, and errors.
  - `HandlerInterface.get_social_data()` maps available getter methods into `SocialData`.

## Data Objects

PageRequestObject (request.py)
  - Encapsulates outgoing request: url, headers, timeout, method.

PageResponseObject (response.py)
  - Encapsulates raw response: status_code, text, headers (ResponseHeaders), binary.

ResponseHeaders (response.py)
  - Thin wrapper over HTTP response headers with typed accessors.

## Supporting Modules

ContentInterface (contentinterface.py)
  - Abstract base defining the content extraction contract:
    get_title(), get_description(), get_date_published(), get_author(),
    get_language(), get_feeds(), get_entries(), get_links(), get_tags(),
    get_thumbnail(), get_social_data()

ContentLinkParser (contentlinkparser.py)
  - HTML link extraction, feed discovery, asset URL collection.

ContentText (contenttext.py)
  - Text cleaning, normalization, and extraction utilities.

UrlLocation (urllocation.py)
  - URL parsing, sanitization, domain extraction, path splitting, and navigation (up()).

DomainCache (domaincache.py)
  - In-memory per-domain cache for crawl rates, policies, and metadata.

WebConfig (webconfig.py)
  - Global runtime configuration singleton.

WebLogger (webtools.py)
  - Logging helpers; also exposes calculate_hash(), calculate_hash_binary(),
    get_default_user_agent(), get_default_headers().

## Utilities (webtoolkit/utils/)

DateUtils — Date parsing and normalization.
PrintLogger / PermanentLogger (logger.py) — Stdout and file logging backends.
MemoryChecker (memorychecker.py) — Memory usage monitoring.
EmailReader (emailreader.py) — Email content reading helper.

## Remote Service (webtoolkit/remoteserver.py)

RemoteServer
  - HTTP client for communicating with an external crawler-buddy daemon.
  - Sends JSON requests, receives JSON responses, maps them back to ContentInterface data.

## Content Moderation (webtoolkit/contentmoderation.py)

UrlAgeModerator — Filters URLs by publication age.
UrlPropertyValidator — Validates URL properties against configurable rules.

## Test Infrastructure (webtoolkit/tests/)

FakeInternet / FakeInternetContents (fakeinternet.py, fakeinternetcontents.py)
  - Intercepts crawler requests in unit tests and returns pre-canned HTML/JSON/RSS from
    domain mocks under webtoolkit/tests/fake/.

FakeResponse (fakeresponse.py) — Synthetic PageResponseObject for unit tests.
MockUrl (mocks.py) — Minimal BaseUrl substitute for unit testing consumers.
