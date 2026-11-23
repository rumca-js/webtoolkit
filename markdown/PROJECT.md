# Architecture & Layers

## Layers
- **Url Layer** (`BaseUrl`, `RemoteUrl`): Entry points for users/consumers representing web resources. Coordinates handlers, requests, caching, and page extraction.
- **Handler Layer** (`handlers/`): Domain- and protocol-specific handlers providing custom parsing, API interaction, and page extraction strategies.
- **Crawler Layer** (`crawlers/`): Network transport abstraction layer (`CrawlerInterface`, `RequestsCrawler`) executing HTTP requests and returning raw responses.
- **Pages Layer** (`pages.py`, `contentinterface.py`): Content representation and extraction objects implementing `ContentInterface`.
- **Remote Layer** (`RemoteUrl`, `RemoteServer`): Client implementation for delegating crawling and parsing to a remote service (`crawler-buddy`).
- **Utilities & Helpers** (`utils/`, `webtools.py`, `domaincache.py`, `contentmoderation.py`, `urllocation.py`): Link sanitization, domain caching, content moderation, date parsing, and logging.

## Content Flow
```
Url (BaseUrl / RemoteUrl)
    │
    ▼
Handler (HandlerInterface / HttpPageHandler / Specialized Handler)
    │
    ▼
Crawler (CrawlerInterface / RequestsCrawler or RemoteServer)
    │
    ▼
Raw Response (PageResponseObject)
    │
    ▼
Page Parser (PageFactory -> HtmlPage / RssPage / OpmlPage / JsonPage)
    │
    ▼
Extracted Content (implements ContentInterface)
```

# Project Layout

## Core Package (`webtoolkit/`)
- `baseurl.py`: Main user-facing class (`BaseUrl`). Inherits from `ContentInterface`, dispatches to handlers and crawlers, and caches responses.
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
- **Testing**:
  - Never make external network requests in unit tests (`tests/unit/`).
  - Keep live network tests in `tests/real/`.
  - Execute test suites via `Makefile` targets: `make test-unit`, `make test-real`, `make test-memory`.

# Developer Notes

- **Poetry Keyring Fix**: If `poetry update` or install commands hang indefinitely, disable the keyring backend:
  ```bash
  export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
  ```
- **Remote Scraping Service**: `RemoteUrl` and `RemoteServer` require a running `crawler-buddy` service instance exposing the JSON IPC protocol.
- **Handler Matching Order**: In `BaseUrl`, specialized handlers match before generic `HttpPageHandler` / `DefaultUrlHandler`. When adding new domain handlers, register them prior to fallback handlers.
- **URL Cleaning**: Link sanitization and tracker removal are handled through `UrlLocation` via `url-cleaner`.
