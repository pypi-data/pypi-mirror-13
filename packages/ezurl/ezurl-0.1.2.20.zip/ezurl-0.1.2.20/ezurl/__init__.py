from collections import OrderedDict

try:
    from urllib.parse import urlunparse
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlunparse
    from urlparse import urlparse



class Url(object):

    """
    This class allows more flexible generation of URLS.
    This prevents the mindless manipulation string that occur
    in projects that require generation of a wide range of urls

    """

    def __init__(self, hostname, scheme="https", querydelimiter="&"):
        """
        Initializes the Url object

        :param hostname: The hostname of the Url
        :param scheme: Optional Scheme selection. Defaults to https
        :param querydelimiter: What the query delimiter is for this URL

        """
        self.schemetrack = scheme
        self.hostnametrack = hostname
        self.pagestrack = list()
        self.querytrack = OrderedDict()
        self.fragmenttrack = ""
        self.querydelimiter = querydelimiter

    def __repr__(self):
        """REPR Implementation"""
        return "<url:{url}>".format(url=str(self))
    
    @property
    def url(self):
        return urlparse(str(self))

    @property
    def scheme(self):
        return self.url.scheme

    @property
    def netloc(self):
        return self.url.netloc

    @property
    def pages(self):
        """Returns a list of pages"""
        return self.pagestrack

    @property
    def path(self):
        """
        Returns str of the Path
        """
        return self.url.path

    @property
    def queries_dict(self):
        return self.querytrack

    @property
    def queries(self):
        return self.url.query

    @property
    def fragments(self):
        return self.url.fragement


    def __str__(self):
        """
        return str object
        """
        return urlunparse((self.schemetrack,
                        self.hostnametrack,
                        self._page_gen(),
                        "",
                        self._query_gen(),
                        self.fragmenttrack))

    def _page_gen(self):
        """
        Generates The String for pages
        """
        track = ""
        for page in self.pagestrack:
            track += "/{page}".format(page=page)
        return track

    def _query_gen(self):
        """Generates The String for queries"""
        querylst = [{x: self.querytrack[x]} for x in self.querytrack]
        if not bool(self.querytrack):
            return ""
        track = "{name}={val}".format(
            name=list(querylst[0].keys())[0],
            val=querylst[0][list(querylst[0].keys())[0]]
        )
        if len(querylst) > 1:
            for x in querylst[1:]:
                track += "{delimiter}{name}={val}".format(
                    delimiter=self.querydelimiter,
                    name=list(x.keys())[0],
                    val=x[list(x.keys())[0]]
                )
        return track

    def page(self, *args):
        """
        Pages takes *args and adds pages in order
        """
        for arg in args:
            self.pagestrack.append(arg)
        return self

    def query(self, listdelimiter="+", **kwargs):
        """
        Url queries

        :param listdelimiter: Specifies what list delimiter should be

        Kwargs (Since its a dictionary) are not ordered. You must call the
        method again if you absolutely need one query
        after another or vice versa.

        """

        for arg in list(kwargs.keys()):
            if (isinstance(kwargs[arg], list)
                    or isinstance(kwargs[arg], tuple)
                    or isinstance(kwargs[arg], set)):
                items = [str(x) for x in kwargs[arg]]
                self.querytrack.update({arg: listdelimiter.join(items)})
            else:
                self.querytrack.update({arg: kwargs.get(arg)})

        return self

    def fragment(self, text):
        """
        Allows for fragments at the end of the url
        """
        self.fragmenttrack = text
        return self

