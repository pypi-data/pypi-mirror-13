from abc import abstractmethod
import datetime
try:
    import urlparse  # python2
except ImportError:
    import urllib.parse as urlparse

import lxml.etree
import lxml.html
import requests
import six


class ScrapedAttribute(object):
    """Base class for scraped attributes.

    When used in a ScrapedPage, it will be converted into an attribute.
    """

    _cleanup = None
    _cleanup_method = None

    def __init__(self, cleanup=None, attribute=None, multiple=False):
        self._cleanup = cleanup
        self.attribute = attribute
        self.multiple = multiple

    @abstractmethod
    def get(self, doc, scraped_page):
        raise NotImplementedError()

    def extract(self, element, scraped_page):
        if self.attribute is None:
            value = element.text_content()
        else:
            value = element.get(self.attribute)
            if value is None:
                return

        return self.perform_cleanups(value, element, scraped_page)

    def perform_cleanups(self, value, element, scraped_page=None):
        if self._cleanup:
            value = self._cleanup(value, element)

        if self._cleanup_method:
            value = self._cleanup_method(scraped_page, value, element)

        return self.cleanup(value, element, scraped_page)

    def cleanup(self, value, elements, scraped_page=None):
        return value

    def __call__(self, func):
        self._cleanup_method = func
        return self

_SCRAPER_CLASSES = {}


class _ScrapedMeta(type):
    """A metaclass for Scraped.

    Converts any ScrapedAttribute attributes to usable properties.
    """
    def __new__(cls, name, bases, namespace):
        for key, value in namespace.items():

            if isinstance(value, ScrapedAttribute):
                def mk_attribute(selector):
                    def method(scraped):
                        return scraped._get_value(selector)
                    return property(method)

                namespace[key] = mk_attribute(value)

        result = super(_ScrapedMeta, cls).__new__(cls, name, bases, namespace)
        _SCRAPER_CLASSES[name] = result
        return result


@six.add_metaclass(_ScrapedMeta)
class ScrapedPage(object):
    _scrape_doc = None
    scrape_url = None
    scrape_args = []
    scrape_arg_defaults = {}

    def __init__(self, *pargs, **kwargs):
        scrape_url = kwargs.pop("scrape_url", None)
        if scrape_url:
            assert not pargs and not kwargs, \
                "scraped_url is mutually exclusive with other arguments"
            self.scrape_url = scrape_url
            self.scrape_args = {}

        else:
            # We can't scrape if we don't actually have a url configured
            if not self.scrape_url:
                raise ValueError("%s.scrape_url needs to be defined" %
                                 type(self).__name__)

            arguments = dict(self.scrape_arg_defaults)
            arguments.update(kwargs)
            arguments.update(zip(self.scrape_args, pargs))
            self.scrape_args = arguments

            self.scrape_url = self.scrape_url % arguments

    def scrape_fetch(self, url):
        return requests.get(url).text

    def _get_value(self, property_scraper):
        if self._scrape_doc is None:
            page = self.scrape_fetch(self.scrape_url)
            self._scrape_doc = lxml.html.fromstring(page)

        return property_scraper.get(self._scrape_doc, scraped_page=self)

    def __repr__(self):
        return "%s(scrape_url=%r)" % (type(self).__name__, self.scrape_url)


class Css(ScrapedAttribute):
    def __init__(self, selector, **kwargs):
        self.selector = selector
        super(Css, self).__init__(**kwargs)

    def get(self, doc, scraped_page):
        assert doc is not None
        elements = doc.cssselect(self.selector)

        if self.multiple:
            values = [self.extract(element, scraped_page)
                      for element in elements]
            return [v for v in values if v is not None]
        elif len(elements):
            return self.extract(elements[0], scraped_page)


class CssFloat(Css):
    def cleanup(self, value, elements, scraped_page=None):
        return float(value)


class CssInt(Css):
    def cleanup(self, value, elements, scraped_page=None):
        return int(value)


class CssDate(Css):
    def __init__(self, selector, date_format, **kwargs):
        self.date_format = date_format
        super(CssDate, self).__init__(selector, **kwargs)

    def cleanup(self, value, elements, scraped_page=None):
        return datetime.datetime.strptime(value, self.date_format)


class CssBoolean(Css):
    def cleanup(self, value, elements, scraped_page=None):
        return True


class CssRaw(Css):
    def extract(self, element, scraped_page):
        value = ''.join(lxml.html.tostring(child, encoding="unicode")
                        for child in element)

        return self.perform_cleanups(value, element, scraped_page)


class CssMulti(Css):
    def __init__(self, selector, cleanup=None, **subselectors):
        super(CssMulti, self).__init__(selector, cleanup=cleanup,
                                       multiple=True)
        self.subselectors = subselectors

    def extract(self, element, scraped_page=None):
        value = {}

        for key, selector in self.subselectors.items():
            value[key] = selector.get(element,
                                      scraped_page=scraped_page)

        return self.perform_cleanups(value, element, scraped_page)


class CssLink(Css):
    def __init__(self, selector, page_factory, **kwargs):
        super(CssLink, self).__init__(selector, attribute="href", **kwargs)
        self.page_factory = page_factory

    def cleanup(self, value, elements, scraped_page=None):
        url = urlparse.urljoin(scraped_page.scrape_url, value)
        factory = (_SCRAPER_CLASSES[self.page_factory]
                   if isinstance(self.page_factory, six.string_types)
                   else self.page_factory)
        return factory(scrape_url=url)
