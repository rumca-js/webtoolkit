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

# Url parsing

Sanitize link and remove trackers:
```
link = UrlLocation.get_cleaned_link(link)
```

Extract domain name:
```
domain = UrlLocation(link).get_domain()
```

Parse link, returns parts of the link [TBD]. It should return .scheme .domain .location .args
```
location = UrlLocation(link)
parsed_data = location.parse_url()
link = location.join(parsed_data) - joins back parsed data into a link
```

Go up in link structure. First to parent location, then to domain, then to domain super.
```
location = UrlLocation(link).up()
```

```
UrlLocation(link).is_onion()
```

# Page definitions

HTML pages
```
page = HtmlPage(url, contents)
page.get_title()
page.get_description()
```

RSS pages
```
page = RssPage(url, contents)
page.get_title()
page.get_description()
page.get_entries()
```

OPML pages
```
page = OpmlPage(url, contents)
page.get_entries()
```

# Content processing

Extracts links from contents
```
ContentLinkParser().get_links()
```

Check if contents if captcha protected
```
ContentInterface().is_captcha_protected()
```

# Standard interfaces

Two standard interfaces
 - CrawlerInterface - Standard interface for crawler implementations
 - HandlerInterface - Allows implementing custom handlers for different use cases

Crawlers are different means of obtaining Internet data. Examples: requests, selenium, playwright, httpx, curlcffi. This package does not provide them, to make it more clean and neat.

Handlers are classes that allows automatic deduction of links, places, video codes from links, or data. Examples: youtube handler can use yt-dlp to obtain channel video list, or obtain channel ID, etc.

Default User agents
```
webtoolkit.default_user_agents
```

Default User headers
```
webtoolkit.default_headers
```

# HTTP processing

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

Response communication is done via JSON
```
json_data = response_to_json(response)
response = json_to_response(json_data)
```

To obtain page contents object:
```
page = PageResponseObject().get_page()   # for example could be HtmlPage
```

# Remote interfaces

You can implement scraping servers yourself. The communication between remotes use PageRequestObject and PageResponseObjects (and encoding them / converting to JSON).

 - RemoteServer - Interface for calling external crawling systems
 - RemoteUrl - Wrapper around RemoteServer for easy access to remote data

# Testing

Provides data and facilities that will aid you in testing.

Do you want to implement new RSS parser? Go ahead, use the data.
