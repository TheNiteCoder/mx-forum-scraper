
from urllib import parse as urlparse

def set_url_arg(url, arg, val):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({arg : str(val)})
    url_parts[4] = urlparse.urlencode(query)
    return urlparse.urlunparse(url_parts)
