# TODO

## High Priority

- [ ] Expose error reporting for social / channel properties
  - baseurl.py, remoteurl.py
  - url returns social properties as a map with no place for errors
  - provide return value with error information, or responses, or streams info

- [ ] Decouple stateful self.response stashing across layers
  - baseurl.py, handlers/handlerhttppage.py
  - BaseUrl and Handler lazily stash and mutate self.response across getter calls,
    causing non-thread-safe side-effects and hidden state coupling
  - make the response acquisition lifecycle explicit or decouple response access
    from class state mutation

- [ ] get_response vs get_responses vs get_streams — one is redundant, clarify API
- [ ] provide playwright crawler(s)
- [ ] provide API to obtain HEAD information
- [ ] is keeping url_builder a good pattern?
- [ ] RemoteUrl could provide get_links (channel url)

## Medium Priority

- [ ] provide missing test cases for urllocation
- [ ] replace UrlLocation.parse_url() raw list with structured type (NamedTuple/dataclass)
  - urllocation.py
  - parse_url() returns a raw list, fragile and index-dependent
- [ ] rationalize response access API (get_response, get_responses, get_streams)
  - baseurl.py
  - ambiguous and overlapping method names for single vs multi-stream responses

## Low Priority

- [ ] support method chaining in UrlLocation (up(), get_clean() should return self)
  - urllocation.py
- [ ] refactor child URL factory in handlers (build_http_url, build_default_url)
  - handlers/defaulturlhandler.py
  - ad-hoc helpers create BaseUrl instances directly inside handler implementations
- [ ] RemoteServer uses get_getj, get_socialj — not valid, not readable, fix it
- [ ] handlerviewyoutube.py — get_feeds should convert channelId to feed url
