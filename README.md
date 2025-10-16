# webtoolkit

Provides classes and tools for Internet data processing.

 - Url parsing
 - HTTP status codes identification
 - Page definitions: HtmlPage, RssPage, OpmlPage, Content interfaces
 - Means of calling crawling systems, Crawling interfaces

Remote crawling interfaces are implmented by [crawler-buddy](https://google.com/rumca-js/crawler-buddy).

Available on [pypi](https://pypi.org/project/webtoolkit).


# Url parsing

Clean link from trackers, sanitize
```
UrlLocation.get_cleaned_link()
```

To obtain domain
```
UrlLocation(link).get_domain()
```

# HTTP processing

Identification of valid codes
```
PageResponseObject().is_valid()
```

Identification of invalid codes
```
PageResponseObject().is_invalid()
```

Some codes might not indicate that this page is valid, and is not invalid. For example if our crawler is throttled because of too many requests we do not know yet if the page is valid, or not.

# Page definitions

Easy access to HTML properties
```
page = HtmlPage(url, contents)
page.get_title()
page.get_description()
```

Easy access to RSS properties
```
page = RssPage(url, contents)
page.get_title()
page.get_description()
page.get_entries()
```

Easy access to Opml properties
```
page = OpmlPage(url, contents)
page.get_entries()
```

# Interfaces

 - RemoteServer - provides means of calling remote crawling systems
 - RemoteUrl - wrapper for RemoteServer, to obtain ready to use data
 - CrawlerInterface - Interface for crawlers
 - HandlerInterface - Allows implementing your own handler
