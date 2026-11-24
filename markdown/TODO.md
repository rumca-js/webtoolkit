# TODO

## High Priority

- [ ] rationalize response access API (get_response, get_responses, get_streams)
  - baseurl.py
  - ambiguous and overlapping method names for single vs multi-stream responses
- [ ] `FakeInternetTestCase.disable_web_pages()` doesn't patch new canonical method names
  - `webtoolkit/tests/fakeinternet.py`
  - when new endpoint methods are added to `RemoteServer`, `disable_web_pages()` must be manually updated, causing hard-to-diagnose test failures
  - consider a registration/decorator mechanism so URL-taking `RemoteServer` methods are auto-patched
- [ ] two pre-existing test failures on `main` pollute CI output
  - `test_get_entries__hackernews` in `test_rsspage.py`
  - `test_get_cleaned_link__stupid_google_link4` in `test_urllocation.py`
  - either `skipTest` them with explanation or fix the underlying issues

## Medium Priority

- [ ] provide missing test cases for urllocation
- [ ] replace UrlLocation.parse_url() raw list with structured type (NamedTuple/dataclass)
  - urllocation.py
  - parse_url() returns a raw list, fragile and index-dependent
- [ ] provide API to obtain HEAD information
- [ ] provide playwright crawler(s)
- handler contains self.p field (page). seems redundant, but is it?

## Low Priority

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

