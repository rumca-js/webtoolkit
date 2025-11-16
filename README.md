# webtoolkit

webtoolkit provides utilities and interfaces for processing and managing Internet data, including URL parsing, HTTP status handling, page type recognition (HTML, RSS, OPML), and support for integrating crawling systems.

Features
 - URL parsing and cleaning
 - HTTP status code classification
 - Page abstraction interfaces (HtmlPage, RssPage, OpmlPage, etc.)
 - Interfaces for integrating with crawling systems

Remote crawling is supported via [crawler-buddy](https://google.com/rumca-js/crawler-buddy). Provides various crawlers and handlers using interfaces from this package.

Available on [pypi](https://pypi.org/project/webtoolkit).

Install by
```
pip install webtoolkit
```

# Url processing

To obtain a Url’s data, you can simply do:
```
url = BaseUrl("https://example.com")

response = url.get_response()

url.get_title()
url.get_description()
url.get_lanugage()
url.get_date_published()
url.get_author()
url.get_feeds()
url.get_entries()
```

BaseUrl automatically detects and supports many different page types, including YouTube, GitHub, Reddit, and others.

Chain of data
```
url = BaseUrl("https://example.com")

response = url.get_response()
handler = url.get_handler()
page = handler.get_page()
```

# Page definitions

BaseUrl supports various page types through different classes

HTML pages
```
page = HtmlPage(url, contents)
page.get_title()
page.get_description()
page.get_lanugage()
page.get_date_published()
page.get_author()
page.get_feeds()
```

RSS pages
```
page = RssPage(url, contents)
page.get_title()
page.get_description()
page.get_lanugage()
page.get_date_published()
page.get_author()
page.get_entries()
```

OPML pages
```
page = OpmlPage(url, contents)
page.get_entries()
```

# Url location processing

Sanitize link and remove trackers:
```
link = UrlLocation.get_cleaned_link(link)
```

Extract domain name:
```
domain = UrlLocation(link).get_domain()
```

Parse and reconstruct links
```
location = UrlLocation(link)
parsed_data = location.parse_url()
link = location.join(parsed_data) - joins back parsed data into a link
```

Navigate up the URL structure
Go up in the link hierarchy — first to the parent path, then to the domain, and finally to the domain root.
```
location = UrlLocation(link).up()
```

```
UrlLocation(link).is_onion()
```

# Content processing

Internet contents can be parsed in various ways.

Extracts links from contents
```
ContentLinkParser(contents).get_links()
```

Obtain text ready for display
```
ContentText(text).htmlify()  # returns text, where http links are turned into HTML links
ContentText(text).noattrs()  # removes HTML attributes
```

Status analysis. Note that from some status we cannot know if page is OK, or not.
```
is_status_code_valid(status_code)   # provides information if input status code indicates the page is OK
is_status_code_invalid(status_code) # provides information if input status code indicates the page is invalid
```

# HTTP processing - requests

Communication is performed via request - response pairs.

Request HTTP object allows to make HTTP call.
```
request = PageRequestObject()
```

To send request to any scraping / crawling server just encode it to GET params
```
url_data = request_encode(request)

json_data = request_to_json(request)  # json
request = json_to_request(json_data)  # json
```

# HTTP processing - response

Check for valid HTTP responses:
```
PageResponseObject().is_valid()
```

Check for invalid HTTP responses:
```
PageResponseObject().is_invalid()
```

To check if response is captcha protected
```
PageResponseObject().is_captcha_protected()
```

Note: Some status codes may indicate uncertain results (e.g. throttling), where the page cannot be confirmed as valid or invalid yet.

To obtain page structure from response, simply
```
PageResponseObject().get_page()   # can return HtmlPage, RssPage, etc.
```

Response communication is done via JSON
```
json_data = response_to_json(response)
response = json_to_response(json_data)
```

To obtain page contents object:
```
page = PageResponseObject().get_page()   # returns type of page, be it HtmlPage, RssPage, etc.
```

# Remote interfaces

You can use existing scraping servers.

 - RemoteUrl - Wrapper around RemoteServer for easy access to remote data. Provides API similar to BaseUrl.

```
url = RemoteUrl("http://192.168.0.168...")
response = url.get_response()

url.get_title()
url.get_description()
url.get_lanugage()
url.get_date_published()
url.get_author()
url.get_feeds()
url.get_entries()
```

The communication between client and server should be through JSON requests and responses.

Other classes

 - RemoteServer - Interface for calling external crawling systems

# Standard interfaces

Two standard interfaces
 - CrawlerInterface - Standard interface for crawler implementations
 - HandlerInterface - Allows implementing custom handlers for different use cases

Crawlers are different means of obtaining Internet data. Examples: requests, selenium, playwright, httpx, curlcffi. This package does not provide them, to make it more clean and neat.

Handlers are classes that allows automatic deduction of links, places, video codes from links, or data. Examples: youtube handler can use yt-dlp to obtain channel video list, or obtain channel ID, etc.

Default User agents
```
webtoolkit.get_default_user_agent()
```

Default User headers
```
webtoolkit.get_default_headers()
```

# Testing

webtoolkit provides data and facilities that will aid you in testing.

You can use them in your project:
 - FakeResponse
 - MockUrl

Project also provides manual tests that check if project works
```
make tests
make tests-unit # run unit tests
make tests-real # tests performed on real internet data
```
