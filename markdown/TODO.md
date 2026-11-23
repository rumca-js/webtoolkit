# TODO

## High Priority

- [ ] Decouple stateful self.response stashing across layers
  - baseurl.py, handlers/handlerhttppage.py
  - BaseUrl and Handler lazily stash and mutate self.response across getter calls,
    causing non-thread-safe side-effects and hidden state coupling
  - make the response acquisition lifecycle explicit or decouple response access
    from class state mutation

## Medium Priority

- [ ] rationalize response access API (get_response, get_responses, get_streams)
  - baseurl.py
  - ambiguous and overlapping method names for single vs multi-stream responses
- [ ] RemoteServer uses get_getj, get_socialj — not valid, not readable, fix it
- [ ] provide missing test cases for urllocation
- [ ] replace UrlLocation.parse_url() raw list with structured type (NamedTuple/dataclass)
  - urllocation.py
  - parse_url() returns a raw list, fragile and index-dependent
- [ ] RemoteUrl could provide get_links (channel url)
- [ ] provide API to obtain HEAD information
- [ ] provide playwright crawler(s)

## Low Priority

- [ ] is keeping url_builder a good pattern?
- [ ] support method chaining in UrlLocation (up(), get_clean() should return self)
  - urllocation.py
- [ ] refactor child URL factory in handlers (build_http_url, build_default_url)
  - handlers/defaulturlhandler.py
  - ad-hoc helpers create BaseUrl instances directly inside handler implementations
- [ ] handlerviewyoutube.py — get_feeds should convert channelId to feed url
