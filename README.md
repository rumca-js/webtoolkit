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
UrlLocation.get_cleaned_link()
```

Extract domain name:
```
UrlLocation(link).get_domain()
```

# HTTP processing

Check for valid HTTP responses:
```
PageResponseObject().is_valid()
```

Check for invalid HTTP responses:
```
PageResponseObject().is_invalid()
```

Note: Some status codes may indicate uncertain results (e.g. throttling), where the page cannot be confirmed as valid or invalid yet.

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

Crawlers are different means of obtaining Internet data. Examples: requests, selenium, playwright, httpx, curlcffi.

Handlers are classes that allows automatic deduction of links, places, video codes from links, or data. Examples: youtube handler can use yt-dlp to obtain channel video list, or obtain channel ID, etc.

Default User agents
```
webtoolkit.default_user_agents
```

Default User headers
```
webtoolkit.default_headers
```

# Remote interfaces

 - RemoteServer - Interface for calling external crawling systems
 - RemoteUrl - Wrapper around RemoteServer for easy access to remote data
