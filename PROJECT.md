# Layers
 - Url (BaseUrl, RemoteUrl)
 - Handler - provide advanced mechanisms to get the data from sites
 - Crawler - tools, and framework API
 - Pages - objects representing file contents, so we have HtmlPage, RssPage, etc.

# Classes
 - baseurl.py - base url, this is what users will be using. Represents Url object
 - urllocation.py - represents web location. Provides link parsing and navigation 
 - response.py - reponses
 - request.py - request
 - statuses.py - HTTP statuses

# Content
 - Url -> Handler -> Crawler -> gets response
 - reponse text is read using Pages factory
 - Content and most of classes implement contentinterface.py

# Remote
 - Often used with crawler-buddy program which provide JSON interface. Here we provide classes to read the network responses. Treated as a standard
