import math

import requests
import re


class ApiException(Exception):
    def __init__(self, response):
        """
        Args:
            response (requests.Response):
        """
        self.response = response

    def __str__(self):
        response = self.response.json()
        if not response or not response.get(u'detail'):
            return "Server responded with unexpected error ({0})".format(self.response.status_code)
        return "Server responded with error ({1}): {0}".format(response.get(u'detail'), self.response.status_code)


class Inquisitor(object):
    """A python interface for the Inquirim API

    Example usage:
    """
    BASE_LIMIT = 10
    # SSL is temporary disabled due to validation problem
    api_url = "http://www.inquirim.com/api"
    token = ""

    def __init__(self, token):
        """

        Args:
            token (str): sting with your authorization token. Please visit

        """
        if not re.match(r'^[a-f0-9]{40}$', token):
            raise ValueError("Invalid token. Please, specify valid token.")
        self.token = token

    def query(self, api_method, request_method="GET", **data):
        """

        Args:
            api_method (str): api method, e.g. `datasets`, `series/FRED.AGEXMFL12A647NCEN0002.Y.USFL`
            request_method (str): HTTP method to use
            **data (dict): query or form parameters

        Returns:
            dict: json deserialized dictionart.
        Raises:
            ApiException: in case of any unexpected API error

        """
        data = {key: value if type(value) is not list else ",".join(value) for key, value in data.items()}
        data['format'] = "json"
        api_path = [self.api_url] + [method for method in api_method.split("/") if method]
        headers = {
            "Authorization": "Token " + self.token,
            "Accept": "application/json"
        }
        if request_method == "GET":
            response = requests.get("/".join(api_path) + "/", data, headers=headers)
        elif request_method == "PUT":
            response = requests.put("/".join(api_path) + "/", data, headers=headers)
        elif request_method == "POST":
            response = requests.post("/".join(api_path) + "/", data, headers=headers)
        else:
            raise ValueError("Wrong request method")
        if response.status_code != 200:
            raise ApiException(response)

        return response.json()

    def query_paginated(self, page_start=1, page_limit=1, **kwargs):
        """
        Make API query with paging.
        Args:
            page_start (int): first page to load
            page_limit (int): maximum number of pages to load
            **kwargs: parameters for query method

        Returns:
            generator object: list with results from every page
        """

        if page_start:
            for source in self.query(page=page_start, **kwargs)['results']:
                yield source
        else:
            sources = self.query(page=1, **kwargs)
            pages = int(math.ceil(float(sources['count']) / self.BASE_LIMIT))
            for page in (1, (pages if pages <= page_limit and page_limit else page_limit) + 1):
                if page > 1:
                    sources = self.query(page=page, **kwargs)
                for source in sources['results']:
                    yield source

    def sources(self, source=None, prefix=None, page=None):
        """
        Load dataset sources in format:

            {
                "prefix": "EU",
                "source": "Eurostat",
                "description": "Eurostat",
                "components": "https://www.inquirim.com/api/datasets/?source=18"
            }
        Examples:
            >>> inquisitor = Inquisitor("your_token")
            >>> inquisitor.sources(page=1)
            [{"prefix": "EU"...}, ...]
            >>> inquisitor.sources()
            <generator object ... >

        Args:
            source (str): filter by source name
            prefix (str): filter bu source prefix
            page (int): if null will load pages until you stop the loop

        Returns:
            generator object
        """
        data = {}
        if source:
            data['source'] = source
        if prefix:
            data['prefix'] = prefix
        return self.query_paginated(api_method="sources", page_start=page, page_limit=1 if page else None, **data)

    def datasets(self, source=None, dataset=None, page=None):
        """
        Load dataset sources in format:
            {
                "dataset": "NAMA_FCS_K",
                "description": "Final consumption aggregates - volumes",
                "components": "https://www.inquirim.com/api/series/?dataset=NAMA_FCS_K",
                "lastupdate": "2015-04-13",
                "last_sync": "2016-01-16T14:08:22",
                "source": {
                    "name": "Eurostat",
                    "detail": "https://www.inquirim.com/api/sources/EU"
                }
            },
        Examples:
            >>> inquisitor = Inquisitor("your_token")
            >>> inquisitor.datasets(page=1)
            [{"prefix": "EU"...}, ...]
            >>> inquisitor.datasets()
            <generator object ... >

        Args:
            source (str): filter by source name
            dataset (str): filter bu dataset name
            page (int): if null will load pages until you stop the loop

        Returns:
            generator object
        """
        data = {}
        if source:
            data['source'] = source
        if dataset:
            data['dataset'] = dataset
        return self.query_paginated(api_method="sources", page_start=page, page_limit=1 if page else None, **data)

    def series(self, page=None, ticker=None, search=None, dataset=None, expand="both", geography=None):
        """
        Filter series by ticker, dataset, or by search terms
        Args:
            page (int): page to load. If None will return generator object with all pages
            ticker (str): ticker name (you can also pass list)
            search (str): search term (e.g. italy productivity)
            dataset (str): dataset name
            expand (str): if 'obs' load ticker name and data values, if 'meta' load only meta info, if 'both'
                load both meta and observations
            geography (str): name of geographical feature

        Returns:
            generator object

        """
        data = {}
        if ticker:
            data['ticker'] = ticker
        if search:
            data['search'] = search
        if dataset:
            data['dataset'] = search
        if expand in ('obs', 'meta', 'both'):
            data['expand'] = expand
        if geography:
            data['geography'] = geography
        return self.query_paginated(api_method="series", page_start=page, page_limit=1 if page else None, **data)

    def basket(self, page=None, expand="obs"):
        """
        Datasets you can edit, download and share.

        Args:
            page (int): page to load. If None will return generator object with all pages
            expand (str): if 'obs' load ticker name and data values, if 'meta' load only meta info, if 'both'
                load both meta and observations

        Returns:
            generator object
        """
        data = {}

        if expand in ('obs', 'meta', 'both'):
            data['expand'] = expand

        return self.query_paginated(api_method="basket", page_start=page, page_limit=1 if page else None, **data)

    def followed(self, page=None, expand="obs"):
        """
        Request the series you follow.

        Args:
            page (int): page to load. If None will return generator object with all pages
            expand (str): if 'obs' load ticker name and data values, if 'meta' load only meta info, if 'both'
                load both meta and observations

        Returns:
            generator object
        """
        data = {}

        if expand in ('obs', 'meta', 'both'):
            data['expand'] = expand

        return self.query_paginated(api_method="followed", page_start=page, page_limit=1 if page else None, **data)
