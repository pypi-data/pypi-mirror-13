# Forager: Feed Finder for Goats
A Python[2|3] utility for finding content feeds on websites.

## Usage
Within the package is the `Forager` class which exposes two methods: `find_feeds` and `find_xmlrpc`. The package also exposes proxy methods to the class, also named `find_feeds` and `find_xmlrpc`.

The `Forager` class can be instantiated with the following optional parameters:
* `max_depth`: This value determines how deeply we will crawl in to the website. When initially crawling we look for links which look like feeds, but some sites (nytimes.com for example) don't publish feeds on their homepage but instead publish them on sub-categories, so by passing a `max_depth` of `2` we will crawl not only the homepage but all pages it links to with `<a>` or `<link>` tags. Defaults to `1`.
* `user_agent`: Some sites don't like the default user-agent used by the `requests` library. Defaults to _'Forager Feed Finder'_.
* `request_delay`: a `datetime.timedelta` object declaring the delay between each http request made to the target site so as to avoid being blocked. Defaults to half a second.
* `request_timeout`: How long to wait for the server to reply to each request before giving up. Defaults to `5` seconds.

Basic usage:
```
import forager
feeds = forager.find_feeds('http://curata.com')
print(feeds)
>>> set([u'http://www.curata.com/blog/feed/'])
```
