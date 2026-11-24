# TODO

## High Priority

- [ ] pre-existing memory test failure pollutes CI output
  - `test_is_valid__warhammer_true` in `test_rsspage.py` — fails in `tearDown` on `memory_increase < 0.1`
  - investigate whether it's a real leak in RSS parsing or a flaky/environment-sensitive threshold



## Medium Priority

- [ ] provide missing test cases for urllocation
- [ ] replace UrlLocation.parse_url() raw list with structured type (NamedTuple/dataclass)
  - urllocation.py
  - parse_url() returns a raw list, fragile and index-dependent
- [ ] provide API to obtain HEAD information
- [ ] provide playwright crawler(s)
- handler contains self.p field (page). seems redundant, but is it?

## Low Priority

- [ ] rationalize response access API (get_response, get_responses, get_streams). They don't look understandble. Maybe their names should be changed. Maybe they should be part of UrlInteface, or HandlerInterface? Similarly get_properties and get_all_properties. Are these OK?
  - baseurl.py
  - ambiguous and overlapping method names for single vs multi-stream responses
- [ ] `FakeInternetTestCase.disable_web_pages()` doesn't patch new canonical method names
  - `webtoolkit/tests/fakeinternet.py`
  - when new endpoint methods are added to `RemoteServer`, `disable_web_pages()` must be manually updated, causing hard-to-diagnose test failures
  - consider a registration/decorator mechanism so URL-taking `RemoteServer` methods are auto-patched
- [ ] Refactor extension mechanism and child URL factory (`url_builder`, `build_http_url`, `build_default_url`)
  - `handlers/defaulturlhandler.py`, `baseurl.py`
  - Current pattern creates cyclical layer dependencies (handlers instantiate top-level `BaseUrl` via `url_builder`), causes resource leaks from unclosed child `BaseUrl` instances, and requires hardcoded `"HttpPageHandler"` hacks to prevent infinite recursion.
  - Implement one of two cleaner patterns:
    - **Option A (Transport / Fetcher Injection)**: Pass a shared `fetcher`/transport context into handlers. Handlers call `self.fetcher.fetch(url, parent_request=self.request)` to obtain raw auxiliary responses without constructing full `BaseUrl` instances or re-triggering handler dispatch.
    - **Option B (Declarative Multi-Source / Container Pattern)**: Handlers declare required endpoints via `get_required_urls()` (e.g. primary watch page + auxiliary dislike API). The orchestrator (`BaseUrl`) fetches all endpoints using its configured crawlers and injects responses into `handler.streams = {url: response}` before property extraction. Handlers remain pure parsers with no fetch or builder responsibilities.
- [ ] support method chaining in UrlLocation (up(), get_clean() should return self)
  - urllocation.py
- [ ] deprecate `j`-suffix aliases on `RemoteServer` (`get_getj`, `get_socialj`, `get_feedsj`, etc.)
  - `webtoolkit/remoteserver.py`
  - aliases still work via delegation but accumulate dead weight; add deprecation warnings to guide downstream cleanup

