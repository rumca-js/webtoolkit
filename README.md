# webtoolkit

Provides classes and tools for Internet data processing.

 - Url parsing
 - HTTP status codes identification
 - Page definitions: HtmlPage, RssPage, OpmlPage, Content interfaces
 - Means of calling crawling systems, Crawling interfaces

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

# Interfaces

 - RemoteServer - Interface for calling external crawling systems
 - RemoteUrl - Wrapper around RemoteServer for easy access to remote data
 - CrawlerInterface - Standard interface for crawler implementations
 - HandlerInterface - Allows implementing custom handlers for different use cases
