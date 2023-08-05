"""Misc utilities.
"""

__author__ = ['Ryan Barrett <webutil@ryanb.org>']

import calendar
import collections
import contextlib
import base64
import datetime
import httplib
import inspect
import json
import logging
import numbers
import os
import re
import socket
import urllib
import urllib2
import urlparse

# These are used in interpret_http_exception() and is_connection_failure(). They
# use dependencies that we may or may not have, so degrade gracefully if they're
# not available.
try:
  import apiclient
  import apiclient.errors
except ImportError:
  apiclient = None

try:
  from oauth2client.client import AccessTokenRefreshError
except ImportError:
  AccessTokenRefreshError = None

try:
  import requests
except ImportError:
  requests = None

try:
  from webob import exc
except ImportError:
  exc = None

try:
  from google.appengine.api import urlfetch_errors
  from google.appengine.runtime import apiproxy_errors
except ImportError:
  urlfetch_errors = None


class Struct(object):
  """A generic class that initializes its attributes from constructor kwargs."""
  def __init__(self, **kwargs):
    vars(self).update(**kwargs)


class CacheDict(dict):
  """A dict that also implements memcache's get_multi() and set_multi() methods.

  Useful as a simple in memory replacement for App Engine's memcache API for
  e.g. get_activities_response() in snarfed/activitystreams-unofficial.
  """
  def get_multi(self, keys):
    keys = set(keys)
    return {k: v for k, v in self.items() if k in keys}

  def set(self, key, val, **kwargs):
    self[key] = val

  def set_multi(self, updates, **kwargs):
    super(CacheDict, self).update(updates)


def to_xml(value):
  """Renders a dict (usually from JSON) as an XML snippet."""
  if isinstance(value, dict):
    if not value:
      return ''
    elems = []
    for key, vals in value.iteritems():
      if not isinstance(vals, (list, tuple)):
        vals = [vals]
      elems.extend(u'<%s>%s</%s>' % (key, to_xml(val), key) for val in vals)
    return '\n' + '\n'.join(elems) + '\n'
  else:
    if value is None:
      value = ''
    return unicode(value)


def trim_nulls(value):
  """Recursively removes dict and list elements with None or empty values."""
  NULLS = (None, {}, [], (), '', set(), frozenset())

  if isinstance(value, dict):
    trimmed = {k: trim_nulls(v) for k, v in value.items()}
    return {k: v for k, v in trimmed.items() if v not in NULLS}
  elif (isinstance(value, (tuple, list, set, frozenset, collections.Iterator)) or
        inspect.isgenerator(value)):
    trimmed = [trim_nulls(v) for v in value]
    ret = (v for v in trimmed if v if v not in NULLS)
    if isinstance(value, collections.Iterator) or inspect.isgenerator(value):
      return ret
    else:
      return type(value)(list(ret))
  else:
    return value


def uniquify(input):
  """Returns a list with duplicate items removed.

  Like list(set(...)), but preserves order.
  """
  if not input:
    return []
  return collections.OrderedDict([x, 0] for x in input).keys()


def get_list(dict, key):
  """Returns a value from a dict as a list.

  If the value is a list or tuple, it's converted to a list. If it's something
  else, it's returned as a single-element list. If the key doesn't exist,
  returns [].
  """
  val = dict.get(key, [])
  return list(val) if isinstance(val, (list, tuple, set)) else [val]


def get_first(dict, key, default=None):
  """Returns the first element of a dict value.

  If the value is a list or tuple, returns the first value. If it's something
  else, returns the value itself. If the key doesn't exist, returns None.
  """
  val = dict.get(key)
  if not val:
    return default
  return val[0] if isinstance(val, (list, tuple)) else val


def tag_uri(domain, name, year=None):
  """Returns a tag URI string for the given domain and name.

  Example return value: 'tag:twitter.com,2012:snarfed_org/172417043893731329'

  Background on tag URIs: http://taguri.org/
  """
  if year is not None:
    year = ',%s' % year
  else:
    year = ''
  return 'tag:%s%s:%s' % (domain, year, name)


_TAG_URI_RE = re.compile('tag:([^,]+)(?:,\d+)?:(.+)$')

def parse_tag_uri(uri):
  """Returns the domain and name in a tag URI string.

  Inverse of tag_uri().

  Returns: (string domain, string name) tuple, or None if the tag URI couldn't
    be parsed
  """
  match = _TAG_URI_RE.match(uri)
  return match.groups() if match else None


def parse_acct_uri(uri, hosts=None):
  """Parses acct: URIs of the form acct:user@example.com .

  Background: http://hueniverse.com/2009/08/making-the-case-for-a-new-acct-uri-scheme/

  Args:
    uri: string
    hosts: sequence of allowed hosts (usually domains). None means allow all.

  Returns: (username, host) tuple

  Raises: ValueError if the uri is invalid or the host isn't allowed.
  """
  parsed = urlparse.urlparse(uri)
  if parsed.scheme and parsed.scheme != 'acct':
    raise ValueError('Acct URI %s has unsupported scheme: %s' %
                     (uri, parsed.scheme))

  try:
    username, host = parsed.path.split('@')
    assert username, host
  except (ValueError, AssertionError):
    raise ValueError('Bad acct URI: %s' % uri)

  if hosts is not None and host not in hosts:
    raise ValueError('Acct URI %s has unsupported host %s; expected %r.' %
                     (uri, host, hosts))

  return username, host


def favicon_for_url(url):
  return 'http://%s/favicon.ico' % urlparse.urlparse(url).netloc


# http://stackoverflow.com/questions/2532053/validate-hostname-string-in-python
HOSTNAME_RE_STR = r'%s(\.%s)*\.?' % ((r'(?!-)[A-Za-z\d-]{1,63}(?<!-)',) * 2)
HOSTNAME_RE = re.compile(HOSTNAME_RE_STR + '$')

def domain_from_link(url):
  """Extracts and returns the meaningful domain from a URL.

  Strips www., mobile., and m. from the beginning of the domain.

  Args:
    url: string

  Returns: string
  """
  parsed = urlparse.urlparse(url)
  if not parsed.hostname and '//' not in url:
    parsed = urlparse.urlparse('http://' + url)

  domain = parsed.hostname
  if domain:
    for subdomain in ('www.', 'mobile.', 'm.'):
      if domain.startswith(subdomain):
        domain = domain[len(subdomain):]
    if domain and HOSTNAME_RE.match(domain):
      return domain

  logging.error('domain_from_link: Invalid domain in %r', url)
  return None


def domain_or_parent_in(input, domains):
  """Returns True if an input domain or its parent is in a set of domains.

  Examples:
    foo, [] => False
    foo, [foo] => True
    foo.bar.com, [bar.com] => True
    foo.bar.com, [.bar.com] => True
    foo.bar.com, [fux.bar.com] => False
    bar.com, [fux.bar.com] => False

  Args:
    input: string domain
    domains: sequence of string domains

  Returns: boolean
  """
  if not input or not domains:
    return False
  elif input in domains:
    return True

  for domain in domains:
    if not domain.startswith('.'):
      domain = '.' + domain
    if input.endswith(domain):
      return True

  return False

def update_scheme(url, handler):
  """Returns a modified string url with the current request's scheme.

  Useful for converting URLs to https if and only if the current request itself
  is being served over https.
  """
  # Instagram can't serve images over SSL, so switch to their S3 or Akamai URLs,
  # which can.
  # https://groups.google.com/d/msg/instagram-api-developers/fB4mwYXZF1c/q9n9gPO11JQJ
  # http://stackoverflow.com/questions/23755897#comment36547383_23755897
  url = re.sub(r'^http://images\.(ak\.)instagram\.com',
               'http://distillery.s3.amazonaws.com', url)
  url = re.sub(r'^http://photos-\w\.(ak\.)instagram\.com',
               'http://igcdn-photos-e-a.akamaihd.net', url)
  return urlparse.urlunparse((handler.request.scheme,) +
                             urlparse.urlparse(url)[1:])


def schemeless(url, slashes=True):
  """Strips the scheme (e.g. 'https:') from a URL.

  Args:
    url: string
    leading_slashes: if False, also strips leading slashes and trailing slash,
      e.g. 'http://example.com/' becomes 'example.com'

  Returns: string URL
  """
  url = urlparse.urlunparse(('',) + urlparse.urlparse(url)[1:])
  if not slashes:
    url = url.strip('/')
  return url


def fragmentless(url):
  """Strips the fragment (e.g. '#foo') from a URL.

  Args:
    url: string

  Returns: string URL
  """
  return urlparse.urlunparse(urlparse.urlparse(url)[:5] + ('',))


def clean_url(url):
  """Removes transient query params (e.g. utm_*) from a URL.

  The utm_* (Urchin Tracking Metrics?) params come from Google Analytics.
  https://support.google.com/analytics/answer/1033867

  Args:
    url: string

  Returns: string, the cleaned url, or None if it can't be parsed
  """
  utm_params = set(('utm_campaign', 'utm_content', 'utm_medium', 'utm_source',
                    'utm_term'))
  try:
    parts = list(urlparse.urlparse(url))
  except (AttributeError, TypeError, ValueError), e:
    logging.info('%s: %s', e, url)
    return None

  query = urllib.unquote_plus(parts[4].encode('utf-8'))
  params = [(name, value) for name, value in urlparse.parse_qsl(query)
            if name not in utm_params]
  parts[4] = urllib.urlencode(params)
  return urlparse.urlunparse(parts)


_LINK_RE = re.compile(ur'\bhttps?://[^\s<>]+\b')
# more complicated alternative:
# http://stackoverflow.com/questions/720113#comment23297770_2102648


def extract_links(text):
  """Returns a list of unique string URLs in the given text.

  URLs in the returned list are in the order they first appear in the text.
  """
  if not text:  # handle None
    return []
  return uniquify(match.group() for match in _LINK_RE.finditer(text))


# Based on kylewm's from redwind:
# https://github.com/snarfed/bridgy/issues/209#issuecomment-47583528
# https://github.com/kylewm/redwind/blob/863989d48b97a85a1c1a92c6d79753d2fbb70775/redwind/util.py#L39
#
# I used to use a more complicated regexp based on
# https://github.com/silas/huck/blob/master/huck/utils.py#L59 , but i kept
# finding new input strings that would make it hang the regexp engine.
_LINKIFY_RE = re.compile(r"""
  \b(?:[a-z]{3,9}:/{1,3})?                   # optional scheme
  (?:[a-z0-9\-]+\.)+[a-z]{2,4}(?::\d{2,6})?  # host and optional port
  (?:(?:/[\w/.\-_~.;:%?@$#&()=+]*)|\b)       # path and query
  """, re.VERBOSE | re.UNICODE | re.IGNORECASE)


def tokenize_links(text, skip_bare_cc_tlds=False):
  """Split text into link and non-link text, returning two lists
  roughly equivalent to the output of re.findall and re.split (with
  some post-processing)

  Args:
    text: string to linkify
    skip_bare_cc_tlds: boolean, whether to skip links of the form
      [domain].[2-letter TLD] with no schema and no path

  Returns: a tuple containing two lists of strings, a list of links
  and list of non-link text
  """
  links = _LINKIFY_RE.findall(text)
  splits = _LINKIFY_RE.split(text)

  for ii in xrange(len(links)):
    # trim trailing punctuation from links
    link = links[ii]
    jj = len(link) - 1
    while (jj >= 0 and link[jj] in '.!?,;:)'
           # allow 1 () pair
           and (link[jj] != ')' or '(' not in link)):
      jj -= 1
      links[ii] = link[:jj + 1]
      splits[ii + 1] = link[jj + 1:] + splits[ii + 1]

    link = links[ii]

    # avoid double linking by looking at preceeding 2 chars
    if (splits[ii].strip().endswith('="')
        or splits[ii].strip().endswith("='")
        or splits[ii + 1].strip().startswith('</a')
        # skip domains with 2-letter TLDs and no schema or path
        or (skip_bare_cc_tlds and re.match('[a-z0-9\-]+\.[a-z]{2}$', link))):
      # collapse link into before text
      splits[ii] = splits[ii] + links[ii]
      links[ii] = None
      continue

  # clean up the output by collapsing removed links
  ii = len(links) - 1
  while ii >= 0:
    if links[ii] is None:
      splits[ii] = splits[ii] + splits[ii + 1]
      del links[ii]
      del splits[ii + 1]
    ii -= 1

  return links, splits


def linkify(text, pretty=False, skip_bare_cc_tlds=False, **kwargs):
  """Adds HTML links to URLs in the given plain text.

  For example: linkify("Hello http://tornadoweb.org!") would return
  Hello <a href="http://tornadoweb.org">http://tornadoweb.org</a>!

  Ignores URLs that are inside HTML links, ie anchor tags that look like
  <a href="..."> .

  Args:
    text: string, input
    pretty: if True, uses pretty_link() for link text

  Returns: string, linkified input
  """

  links, splits = tokenize_links(text, skip_bare_cc_tlds)
  result = []

  for ii in xrange(len(links)):
    result.append(splits[ii])

    url = href = links[ii]
    if not href.startswith('http://') and not href.startswith('https://'):
      href = 'http://' + href

    if pretty:
      result.append(pretty_link(href, **kwargs))
    else:
      result.append(u'<a href="%s">%s</a>' % (href, url))
  result.append(splits[-1])
  return ''.join(result)


def pretty_link(url, text=None, keep_host=True, glyphicon=None, attrs=None,
                new_tab=False, max_length=None):
  """Renders a pretty, short HTML link to a URL.

  In the the link text, Removes the leading http(s)://[www.] and ellipsizes at
  the end if necessary.

  The default maximum length follow's Twitter's rules: full domain plus 15
  characters of path (including leading slash).
  https://dev.twitter.com/docs/tco-link-wrapper/faq
  https://dev.twitter.com/docs/counting-characters

  Args:
    url: string
    text: string, optional
    keep_host: if False, remove the host from the link text
    glyphicon: string glyphicon to render after the link text, if provided.
      Details: http://glyphicons.com/
    attrs: dict of attributes => values to include in the a tag. optional
    new_tab: boolean, include target="_blank" if True
    max_length: int, max link text length in characters. ellipsized beyond this.
  """
  if text:
    if max_length is None:
      max_length = 30
  else:
    # use shortened version of URL as link text
    parsed = urlparse.urlparse(url)
    text = url[len(parsed.scheme) + 3:]  # strip scheme and ://
    host_len = len(parsed.netloc)
    if (keep_host and not parsed.params and not parsed.query and not parsed.fragment):
      text = text.strip('/')  # drop trailing slash
    elif not keep_host:
      text = text[host_len + 1:]
      host_len = 0
    if text.startswith('www.'):
      text = text[4:]
      host_len -= 4
    if max_length is None:
      max_length = host_len + 15

  if max_length and len(text) > max_length:
    text = text[:max_length] + '...'

  if glyphicon is not None:
    text += ' <span class="glyphicon glyphicon-%s"></span>' % glyphicon
  attr_str = (''.join('%s="%s" ' % (attr, val) for attr, val in attrs.items())
              if attrs else '')
  target = 'target="_blank" ' if new_tab else ''
  return ('<a %s%shref="%s">%s</a>' % (attr_str, target, url, text))


class SimpleTzinfo(datetime.tzinfo):
  """A simple, DST-unaware tzinfo subclass.
  """

  offset = datetime.timedelta(0)

  def utcoffset(self, dt):
    return self.offset

  def dst(self, dt):
    return datetime.timedelta(0)


def parse_iso8601(str):
  """Parses an ISO 8601 or RFC 3339 date/time string and returns a datetime.

  Time zone designator is optional. If present, the returned datetime will be
  time zone aware.

  Args:
    str: string ISO 8601 or RFC 3339, e.g. '2012-07-23T05:54:49+00:00'

  Returns: datetime
  """
  # grr, this would be way easier if strptime supported %z, but evidently that
  # was only added in python 3.2.
  # http://stackoverflow.com/questions/9959778/is-there-a-wildcard-format-directive-for-strptime
  try:
    base, zone = re.match('(.{19})([+-]\d{2}:?\d{2})?', str).groups()
  except AttributeError, e:
    raise ValueError(e)

  tz = None
  if zone:
    zone = zone.replace(':', '')
    tz = SimpleTzinfo()
    tz.offset = (datetime.datetime.strptime(zone[1:], '%H%M') -
                 datetime.datetime.strptime('', ''))
    if zone[0] == '-':
      tz.offset = -tz.offset

  return datetime.datetime.strptime(base, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=tz)


def maybe_iso8601_to_rfc3339(input):
  """Tries to convert an ISO 8601 date/time string to RFC 3339.

  The formats are similar, but not identical, eg. RFC 3339 includes a colon in
  the timezone offset at the end (+0000 instead of +00:00), but ISO 8601
  doesn't.

  If the input can't be parsed as ISO 8601, it's silently returned, unchanged!

  http://www.rfc-editor.org/rfc/rfc3339.txt
  """
  try:
    return parse_iso8601(input).isoformat('T')
  except (ValueError, TypeError):
    return input


def maybe_timestamp_to_rfc3339(input):
  """Tries to convert a string or int UNIX timestamp to RFC 3339."""
  try:
    return datetime.datetime.fromtimestamp(int(input)).isoformat('T')
  except (ValueError, TypeError):
    return input


def to_utc_timestamp(input):
  """Converts a datetime to a float POSIX timestamp (seconds since epoch)."""
  if not input:
    return None

  timetuple = list(input.timetuple())
  # timetuple() usually strips microsecond
  timetuple[5] = float(int(timetuple[5])) + float(input.microsecond) / 1000000
  return calendar.timegm(timetuple)

def ellipsize(str, words=14, chars=140):
  """Truncates and ellipsizes str if it's longer than words or chars.

  Words are simply tokenized on whitespace, nothing smart.
  """
  split = str.split()
  if len(split) <= words and len(str) <= chars:
    return str
  return ' '.join(split[:words])[:chars-3] + '...'


def add_query_params(url, params):
  """Adds new query parameters to a URL. Encodes as UTF-8 and URL-safe.

  Args:
    url: string URL or urllib2.Request. May already have query parameters.
    params: dict or list of (string key, string value) tuples. Keys may repeat.

  Returns: string URL
  """
  is_request = isinstance(url, urllib2.Request)
  if is_request:
    req = url
    url = req.get_full_url()

  if isinstance(params, dict):
    params = params.items()

  # convert to list so we can modify later
  parsed = list(urlparse.urlparse(url))
  # query params are in index 4
  params = set((k, unicode(v).encode('utf-8')) for k, v in params)
  parsed[4] += ('&' if parsed[4] else '') + urllib.urlencode(list(params))
  updated = urlparse.urlunparse(parsed)

  if is_request:
    return urllib2.Request(updated, data=req.get_data(), headers=req.headers)
  else:
    return updated


def get_required_param(handler, name):
  val = handler.request.get(name)
  if not val:
    handler.abort(400, 'Missing required parameter: %s' % name)
  return val


def dedupe_urls(urls):
  """Normalizes and de-dupes http(s) URLs.

  Converts domain to lower case, adds trailing slash when path is empty, and
  ignores scheme (http vs https), preferring https. Preserves order.

  Domains are case insensitive, even modern domains with Unicode/punycode
  characters:

  http://unicode.org/faq/idn.html#6
  https://tools.ietf.org/html/rfc4343#section-5

  As examples, http://foo/ and https://FOO are considered duplicates, but
  http://foo/bar and http://foo/bar/ aren't.

  Background: https://en.wikipedia.org/wiki/URL_normalization

  TODO: port to https://pypi.python.org/pypi/urlnorm

  Args:
    urls: sequence of string URLs

  Returns:
    sequence of string URLs
  """
  result = []

  for url in urls:
    p = urlparse.urlsplit(url)
    # normalize domain (hostname attr is lower case) and path
    norm = [p.scheme, p.hostname, p.path or '/', p.query, p.fragment]

    if p.scheme == 'http' and urlparse.urlunsplit(['https'] + norm[1:]) in result:
      continue
    elif p.scheme == 'https':
      try:
        result.remove(urlparse.urlunsplit(['http'] + norm[1:]))
      except ValueError:
        pass

    url = urlparse.urlunsplit(norm)
    if url not in result:
      result.append(url)

  return result


def if_changed(cache, updates, key, value):
  """Returns a value if it's different from the cached value, otherwise None.

  Values that evaluate to False are considered equivalent to None, in order to
  save cache space.

  If the values differ, updates[key] is set to value. You can use this to
  collect changes that should be made to the cache in batch. None values in
  updates mean that the corresponding key should be deleted.

  Args:
    cache: any object with a get(key) method
    updates: mapping (e.g. dict)
    key: anything supported by cache
    value: anything supported by cache

  Returns: value or None
  """
  if cache is None:
    return value
  cached = cache.get(key)

  # normalize to None
  if not value:
    value = None
  if not cached:
    cached = None

  if value == cached:
    return None

  updates[key] = value
  return value


def generate_secret():
  """Generates a URL-safe random secret string.

  Uses App Engine's os.urandom(), which is designed to be cryptographically
  secure: http://code.google.com/p/googleappengine/issues/detail?id=1055

  Args:
    bytes: integer, length of string to generate

  Returns: random string
  """
  return base64.urlsafe_b64encode(os.urandom(16))


def is_int(arg):
  """Returns True if arg can be converted to an integer, False otherwise."""
  try:
    as_int = int(arg)
    return as_int == arg if isinstance(arg, numbers.Number) else True
  except (ValueError, TypeError):
    return False


def interpret_http_exception(exception):
  """Extracts the status code and response from different HTTP exception types.

  Args:
    exception: one of:
      apiclient.errors.HttpError
      exc.WSGIHTTPException
      gdata.client.RequestError
      oauth2client.client.AccessTokenRefreshError
      requests.HTTPError
      urllib2.HTTPError
      urllib2.URLError

  Returns: (string status code or None, string response body or None)
  """
  e = exception
  code = body = None

  if exc and isinstance(e, exc.WSGIHTTPException):
    code = e.code
    body = e.plain_body({})

  elif isinstance(e, urllib2.HTTPError):
    code = e.code
    try:
      body = e.read() or getattr(e, 'body')
      if body:
        # store a copy inside the exception because e.fp.seek(0) to reset isn't
        # always available.
        e.body = body
    except AttributeError, ae:
      if not body:
        body = e.reason

  elif isinstance(e, urllib2.URLError):
    body = e.reason

  elif requests and isinstance(e, requests.HTTPError):
    code = e.response.status_code
    body = e.response.text

  elif apiclient and isinstance(e, apiclient.errors.HttpError):
    code = e.resp.status
    body = e.content

  elif (AccessTokenRefreshError and isinstance(e, AccessTokenRefreshError) and
        str(e).startswith('invalid_grant')):
    code = '401'

  # hack to interpret gdata.client.RequestError since gdata isn't a dependency
  elif e.__class__.__name__ == 'RequestError':
    code = getattr(e, 'status')
    body = getattr(e, 'body')

  if code:
    code = str(code)
  orig_code = code
  if code or body:
    logging.warning('Error %s, response body: %s', code, body)

  # silo-specific error_types that should disable the source.
  #
  # instagram
  if body and ('OAuthAccessTokenException' in body or      # revoked access
               'APIRequiresAuthenticationError' in body):  # account deleted
    code = '401'

  # facebook
  # https://developers.facebook.com/docs/graph-api/using-graph-api/#errors
  try:
    error = json.loads(body).get('error', {})
    if not isinstance(error, dict):
      error = {'message': `error`}
  except BaseException:
    error = {}

  type = error.get('type')
  message = error.get('message')
  if not isinstance(message, basestring):
    message = `message`
  err_code = error.get('code')
  err_subcode = error.get('error_subcode')
  if ((type == 'OAuthException' and
       # have to use message, not error code, since some error codes are for
       # both auth and non-auth errors, e.g. we've gotten code 100 for both
       # "This authorization code has expired." and "Too many IDs. ..."
       ('token provided is invalid.' in message or
        'authorization code has expired.' in message or
        'the user is not a confirmed user.' in message or
        'Permissions error' == message
       )) or
      (type == 'FacebookApiException' and 'Permissions error' in message) or
      (err_code in (102, 190) and err_subcode in (458, 460, 463))):
    code = '401'

  if code == '401' and error.get('is_transient'):
    code = orig_code if orig_code != '401' else '402'

  if orig_code != code:
    logging.info('Converting code %s to %s', orig_code, code)

  return code, body


@contextlib.contextmanager
def ignore_http_4xx_error():
  try:
    yield
  except BaseException, e:
    code, _ = interpret_http_exception(e)
    if not (code and int(code) / 100 == 4):
      raise


def is_connection_failure(exception):
  """Returns True if the given exception is a network connection failure.

  ...False otherwise.
  """
  if (isinstance(exception, (
      apiproxy_errors.CancelledError,
      apiproxy_errors.DeadlineExceededError,
      httplib.ImproperConnectionState,
      httplib.NotConnected,
      requests.ConnectionError,
      requests.Timeout,
      socket.error,  # base class for all socket exceptions, including socket.timeout
      urlfetch_errors.DownloadError,  # base class, e.g. for DeadlineExceededError
      urlfetch_errors.InternalTransientError,
      )) or
      (isinstance(exception, urllib2.URLError) and
       isinstance(exception.reason, socket.error)) or
      (isinstance(exception, httplib.HTTPException) and
       'Deadline exceeded' in exception.message)
     ):
    logging.info('Connection failure: ', exc_info=True)
    return True

  return False
