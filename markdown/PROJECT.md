# Architecture & Layers

## Layers
- **Url Layer** (`BaseUrl`, `RemoteUrl`): Entry points for users/consumers representing web resources. Coordinates handlers, requests, caching, and page extraction.
- **Handler Layer** (`handlers/`): Domain- and protocol-specific handlers providing custom parsing, API interaction, and page extraction strategies. Handlers may be compound/multi-source, managing response containers (`streams`) mapping URLs to `PageResponseObject`s.
- **Crawler Layer** (`crawlers/`): Network transport abstraction layer (`CrawlerInterface`, `RequestsCrawler`) executing HTTP requests and returning raw responses.
- **Pages Layer** (`pages.py`, `contentinterface.py`): Content representation and extraction objects implementing `ContentInterface`.
- **Remote Layer** (`RemoteUrl`, `RemoteServer`): Client implementation for delegating crawling and parsing to a remote service (`crawler-buddy`).
- **Utilities & Helpers** (`utils/`, `webtools.py`, `domaincache.py`, `contentmoderation.py`, `urllocation.py`): Link sanitization, domain caching, content moderation, date parsing, and logging.

## Content Flow
```
Url (BaseUrl / RemoteUrl)
    │
    ▼
Handler (HandlerInterface / Compound / Specialized Handler)
    │
    ├─► Crawler(s) (RequestsCrawler / RemoteServer)
    │       │
    │       ▼
    │   Response Container (streams: {url: PageResponseObject})
    │       │
    │       ├─► Primary Response (self.url) ──► Page Parser (PageFactory) ──► get_response() / ContentInterface
    │       └─► Auxiliary Responses (APIs)  ──► Social Parser             ──► get_social_data() (SocialData)
    ▼
Extracted Content / Metadata
```

# Project Layout

## Core Package (`webtoolkit/`)
- `baseurl.py`: Main user-facing class (`BaseUrl`). Inherits from `ContentInterface`, dispatches to handlers and crawlers, and caches responses.
- `socialdata.py`: Structured social metrics and source error reporting dataclasses (`SocialData`, `SocialSourceResult`).
- `remoteurl.py`: Remote URL consumer (`RemoteUrl`) interacting with external crawler services.
- `remoteserver.py`: Connection and client communication wrapper for remote crawler daemons (`crawler-buddy`).
- `urllocation.py`: URL parsing, sanitization, domain extraction, and hierarchical navigation (`UrlLocation`).
- `contentinterface.py`: Abstract base interface defining content extraction methods (`get_title()`, `get_description()`, `get_date_published()`, etc.).
- `pages.py`: Page representations (`HtmlPage`, `RssPage`, `OpmlPage`, `JsonPage`, `XmlPage`, `DefaultContentPage`) and `PageFactory`.
- `contentlinkparser.py`: HTML link parsing, feed discovery, asset link extraction.
- `contenttext.py`: Text extraction, cleaning, and normalization utilities.
- `contentmoderation.py`: Content moderation and age filtering (`UrlAgeModerator`, `UrlPropertyValidator`).
- `domaincache.py`: In-memory cache for per-domain information, rates, and policies (`DomainCache`).
- `request.py`: Encapsulates HTTP request data (`PageRequestObject`).
- `response.py`: Encapsulates HTTP response data and headers (`PageResponseObject`, `ResponseHeaders`).
- `statuses.py`: HTTP status code mapping and classification utilities.
- `webconfig.py`: Global runtime configuration (`WebConfig`).
- `webtools.py`: Helper functions for hashing, date parsing, and logging (`WebLogger`).

## Subpackages
- **Handlers (`webtoolkit/handlers/`)**: `HandlerInterface`, `DefaultUrlHandler`, `HttpPageHandler`, `CrawlerCaller`, and platform handlers (YouTube, Odysee, Reddit, GitHub, Hacker News, Twitter, 4chan, Internet Archive, Return YouTube Dislike).
- **Crawlers (`webtoolkit/crawlers/`)**: `CrawlerInterface`, default headers/user-agent generation, and `RequestsCrawler`.
- **Utilities (`webtoolkit/utils/`)**: `DateUtils`, `PrintLogger`, `PermanentLogger`, `MemoryChecker`, and `EmailReader`.
- **Test Harness (`webtoolkit/tests/`)**: Mock infrastructure (`fakeinternet.py`, `fakeresponse.py`, `mocks.py`, domain mocks in `fake/`).

## Test Suite (`tests/`)
- `tests/unit/`: Isolated unit tests using fake network mocks.
- `tests/real/`: Integration tests interacting with real network endpoints.
- `tests/memory/`: Memory consumption and leak tests.

# Extensions

`BaseUrl` is designed to be extended by downstream applications (e.g., a custom `Url` class) to inject domain-specific crawler selection, rate limiting, and custom handler registries.

To ensure child requests spawned by handlers honor the extension:
- `url_builder` (pointing to the `BaseUrl` subclass) is injected into handlers.
- `DefaultUrlHandler.build_http_url(url)`: Creates a child `url_builder` instance forced to `HttpPageHandler` to fetch raw content (HTML/JSON) without recursive handler dispatch.
- `DefaultUrlHandler.build_default_url(url)`: Creates a child `url_builder` instance using standard handler resolution according to the subclass's configuration.

# Coding Conventions

- **Python Version**: Python 3.9+.
- **Formatting**: Format code using `black` (`poetry run black webtoolkit`).
- **Naming Conventions**:
  - Files and modules: `snake_case.py`.
  - Classes and Exceptions: `PascalCase`.
  - Functions and methods: `snake_case()`.
  - Constants: `UPPER_CASE`.
- **Interfaces & Extensibility**:
  - Content extractors must inherit from `ContentInterface` or `DefaultContentPage`.
  - Extractors should return `None` or empty containers on missing data rather than raising unhandled exceptions.
  - Return typed objects (`datetime` for dates, `list[str]` for tags/feeds).
  - Multi-source / compound handlers must store fetched responses in `self.streams: dict[str, PageResponseObject]` keyed by URL, rather than discarding auxiliary responses or mutating ad-hoc fields.
  - **Transport Agnosticism**: All fetch mechanisms (HTTP GET, POST/GraphQL, Playwright, CLI/subprocesses like `yt-dlp`, or remote daemons) encapsulate results into `PageResponseObject` before populating `streams`. APIs (`get_response`, `get_responses`, `get_streams`, `get_social_data`) operate exclusively on `PageResponseObject` instances, decoupled from transport details.
  - `get_response()` returns the primary content response (matching `self.url` or primary entry in `streams`).
  - `get_social_data()` aggregates engagement metrics across relevant responses in `streams`, capturing endpoint status in `SocialData.sources: list[SocialSourceResult]`.
- **Testing**:
  - The project uses the standard library `unittest` runner (not `pytest`).
  - Never make external network requests in unit tests (`tests/unit/`).
  - Keep live network tests in `tests/real/`.
  - Always execute test suites inside Poetry environment (`poetry run`) or via `Makefile` targets.
  - Commands:
    - Run all unit tests: `make test-unit` (or `poetry run python -u -m unittest discover -s tests/unit -v`)
    - Run a single test file: `poetry run python -m unittest tests/unit/test_<name>.py`
    - Run a specific test method: `poetry run python -m unittest tests.unit.test_<name>.<ClassName>.<test_method>`
    - Run live integration tests: `make test-real`
    - Run memory leak tests: `make test-memory`

# Developer Notes

- **Poetry Keyring Fix**: If `poetry update` or install commands hang indefinitely, disable the keyring backend:
  ```bash
  export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
  ```
- **Remote Scraping Service**: `RemoteUrl` and `RemoteServer` require a running `crawler-buddy` service instance exposing the JSON IPC protocol.
- **Handler Matching Order**: In `BaseUrl`, specialized handlers match before generic `HttpPageHandler` / `DefaultUrlHandler`. When adding new domain handlers, register them prior to fallback handlers.
- **URL Cleaning**: Link sanitization and tracker removal are handled through `UrlLocation` via `url-cleaner`.
