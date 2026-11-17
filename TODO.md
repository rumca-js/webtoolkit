# TODO

## High Priority

- [ ] **Implement Context Manager for Resource Management (`BaseUrl.close`)**
  - **Location**: `webtoolkit/baseurl.py`
  - **Issue**: Calling `.close()` manually is error-prone when exceptions occur, risking leaked response streams and network sockets.
  - **Action**: Implement `__enter__` and `__exit__` on `BaseUrl` and handlers (`with BaseUrl(...) as url: ...`) for deterministic exception-safe cleanup.

- [ ] **Expose Error Reporting for Social / Channel Properties**
  - **Location**: `webtoolkit/baseurl.py`, `webtoolkit/remoteurl.py`
  - **Issue**: url returns social properties as a map. does not have any place for errors.
  - **Action**: Provide return value with error information, or responses, or streams information

- [ ] **Decouple Stateful `self.response` Stashing Across Layers**
  - **Location**: `webtoolkit/baseurl.py`, `webtoolkit/handlers/handlerhttppage.py`
  - **Issue**: `BaseUrl` and `Handler` lazily stash and mutate `self.response` across getter calls, causing non-thread-safe side-effects and hidden state coupling.
  - **Action**: Make the response acquisition lifecycle explicit or decouple response access from class state mutation.

 - get_response vs get_responses vs get_streams. one is redundant. which is api?
 - provide playwright crawler(s)

## Medium Priority

- provide missing test cases for urllocation
- [ ] **Replace `UrlLocation.parse_url()` Raw List with Structured Type**
  - **Location**: `webtoolkit/urllocation.py`
  - **Issue**: `parse_url()` returns a raw Python `list` (`["https", "://", ...]`), which is fragile and index-dependent.
  - **Action**: Return a typed `NamedTuple` or `@dataclass` (e.g. `ParsedUrl(scheme, host, port, path, query, fragment)`).

- [ ] **Rationalize Response Access API (`get_response`, `get_responses`, `get_streams`)**
  - **Location**: `webtoolkit/baseurl.py`
  - **Issue**: Ambiguous and overlapping method names between single response access and multi-stream responses.
  - **Action**: Unify and standardize response accessor names (e.g. `get_response()` for main page, `get_streams()` / `get_all_responses()` for multi-stream media).

## Low Priority

- [ ] **Support Method Chaining in `UrlLocation`**
  - **Location**: `webtoolkit/urllocation.py`
  - **Issue**: Navigation and transformation methods (`up()`, `get_clean()`) do not consistently return `self` or a new instance.
  - **Action**: Return `self` from mutating operations to enable fluent calls like `UrlLocation(url).up().get_domain()`.

- [ ] **Refactor Child URL Factory in Handlers (`build_http_url`, `build_default_url`)**
  - **Location**: `webtoolkit/handlers/defaulturlhandler.py`
  - **Issue**: Ad-hoc helper methods create `BaseUrl` instances directly inside handler implementations.
  - **Action**: Move child URL creation into a dedicated factory helper or standardize child request instantiation.

- [ ] RemoteServer uses get\_getj, get\_socialj functions which are not valid, not readable, not clean. fix it
- [ ] handlerviewyoutube.py - get_feeds should be able to use some function to convert channelId to feed (or channel handler)
