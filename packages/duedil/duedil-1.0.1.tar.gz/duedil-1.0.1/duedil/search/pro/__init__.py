from .company import CompanySearchResult
from .director import DirectorSearchResult
from .. import SearchResouceList

from collections import Sequence
try:
    from urllib import urlencode
    import urlparse
except ImportError:
    from urllib.parse import urlencode
    from urllib import parse as urlparse

class ProSearchResourceList(SearchResouceList):

    def __init__(self, results, result_klass, client):
        super(ProSearchResourceList, self).__init__(results, result_klass, client)
        self._next_url = None
        # look at the property below
        self.next_url = results
        page = results.get('response', {}).get('pagination', {})
        self._length = page.get('total', len(self.result_list))

    def __str__(self):
        return "Pro Search Result List - total: {}".format(len(self))

    @property
    def next_url(self):
        return self._next_url

    @next_url.setter
    def next_url(self, value):
        page = value.get('response', {}).get('pagination', {})
        if page:
            self._next_url = page.get('next_url')
        else:
            self._next_url = ''


    def next(self):
        # should get the next set of results
        # update the internal list
        if not self.fetched_all_results():
            next_set = self.client.get(*self.parse_next_url())
            # check the property - this does a .extend()!
            self.result_list = next_set
            # update the next_url
            self.next_url = next_set
        else:
            raise StopIteration

    def __len__(self):
        return self._length

    def __getitem__(self, key):
        if type(key) is int:
            if key < 0:
                # key should be negative so +- equals -
                key = self._length + key
            if key >= self._length:
                raise IndexError()
            try:
                return self.result_list[key]
            except IndexError:
                # key is not in current cut of data
                # therefore loop with .next until result?
                self._update_next_url(1, key)
                return self.client.get(*self.parse_next_url())
        elif type(key) is slice:
            # this needs to be done to limit for loop iteration...
            raise NotImplementedError("Results don't support slicing at this time")
        else:
            raise TypeError()

    def __iter__(self):
        for result in self.result_list:
            yield result
            # get the last one and extend the list
            # if self.result_list[-1] is result:
            #     self.next()


    def __contains__(self, result):
        while not self.fetched_all_results():
            if result in self.result_list:
                return True
            # this could be hugely expensive, so get as many as possible. Duedil only allow upto a limit of 100
            self._update_next_url(limit=100)
            self.next()
        return False

    def fetched_all_results(self):
        return len(self.result_list) >= len(self)

    def _update_next_url(self, limit=None, offset=None):
        scheme, netloc, path, query_string, frag = urlparse.urlsplit(self._next_url)
        query_params = urlparse.parsed_qs(query_string)
        if limit:
            query_params['limit'] = [limit]
        if offset:
            query_params['offset'] = [offset]
        self._next_url = urlparse.urlunsplit((scheme, netloc, path, urlencode(query_params, doseq=True), frag))

    def parse_next_url(self):
        parsed_url = urlparse.urlsplit(self._next_url)
        path = parsed_url.path.rsplit('/', 1)[-1]
        if path.endswith('.json'):
            path = path[:-len('.json')] # grab the last part of the path
        query_params = dict(urlparse.parse_qsl(parsed_url.query))
        return path, query_params
