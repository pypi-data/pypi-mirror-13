# Forager: Feed Finder for Goats
A Python[2|3] utility for finding content feeds on websites.

## Usage
Within the package is the `Forager` class which exposes two methods: `find_feeds` and `find_xmlrpc`. The package also exposes proxy methods to the class, also named `find_feeds` and `find_xmlrpc`.

The `Forager` class can be instantiated with the following optional parameters:
* `max_depth`: This value determines how deeply we will crawl in to the website. When initially crawling we look for links which look like feeds, but some sites (nytimes.com for example) don't publish feeds on their homepage but instead publish them on sub-categories, so by passing a `max_depth` of `2` we will crawl not only the homepage but all pages it links to with `<a>` or `<link>` tags. Defaults to `1`.
* `user_agent`: Some sites don't like the default user-agent used by the `requests` library. Defaults to _'Forager Feed Finder'_.
* `request_delay`: a `datetime.timedelta` object declaring the delay between each http request made to the target site so as to avoid being blocked. Defaults to 1/5 of a second.
* `request_timeout`: How long to wait for the server to reply to each request before giving up. Defaults to `5` seconds.

**Basic usage:**

```
import forager
feeds = forager.find_feeds('http://curata.com')
print(feeds)
>>> set([u'http://www.curata.com/blog/feed/'])
```

**More complex usage using auth and other optional params:**

The first of the auth's will match a specific url; the second will match anything on a given domain; and the third will match anything with 'pancakes' in the url. The search order is the same: exact url first, domain match second, then finally try treating each key in the `auths` dict as a regex to match the current url.
```
import forager
import requests
from datetime import timedelta

auths = {
  'http://blah.com/some_specific_page.html': requests.HTTPBasicAuth(username='user2', password='garble'),
  'blah.com': requests.HTTPBasicAuth(username='user1', password='garble'),
  r'^https?://.*?pancakes.*?$': requests.HTTPBasicAuth(username='user3', password='garble'),
}

f = Forager(
  max_depth=2,
  user_agent='some other user agent',
  request_delay=timedelta(100000),  # delay 1/10 of a second between each request opposed to the default 1/5
  request_timeout=1,  # time out after 1 second instead of the default of 5
  auths=auths
  )
f.find_feeds('blah.com')
```
  
**Exceptions:**

Exceptions raised by the library will attach the requests response object to the Exception object.
```
import forager
try:
  forager.find_feeds('http://blah.com/something-protected/')
except exceptions.Unauthorized as e:
  print("I need a password to connect to {url}".format(url=e.response.url))
```
