from collections import OrderedDict

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
        self.scheme = scheme
        self.hostname = hostname
        self.pagestrack = list()
        self.querytrack = OrderedDict()
        self.fragmenttrack = ""
        self.querydelimiter = querydelimiter

    def __repr__(self):
        """REPR Implementation"""
        return "<url:{url}>".format(url=str(self))

    def __str__(self):
        return "{scheme}://{hostname}{pages}{query}{fragment}".format(
            scheme=self.scheme,
            hostname=self.hostname,
            pages=self._page_gen(),
            query=self._query_gen(),
            fragment=self.fragmenttrack
        )

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
        querylst = [{x:self.querytrack[x]} for x in self.querytrack]
        if not bool(self.querytrack):
            return ""
        track = "?{name}={val}".format(
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
        self.fragmenttrack = "#{}".format(text)
        return self
