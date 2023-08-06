
from importlib import import_module
from collections import Sequence



class SearchResource(object):
    attribute_names = None
    locale = 'uk'
    id = None
    path = None
    result_obj = {}

    def __init__(self, client, id=None, locale='uk', load=False, **kwargs):
        if not self.attribute_names:
            raise NotImplementedError(
                "Resources must include a list of allowed attributes")

        self.id = id
        assert(locale in ['uk', 'roi'])
        self.locale = locale
        self.client = client
        self.should_load = True if load else False
        if load:
            self.load()

        if kwargs:
            self._set_attributes(**kwargs)

    def _set_attributes(self, missing=False, **kwargs):
        for k, v in kwargs.items():
            if k in self.attribute_names:
                self.__setattr__(k, v)

        if missing is True:
            for allowed in self.attribute_names:
                if allowed not in kwargs:
                    self.__setattr__(allowed, None)

    def load(self):
        result = self.client.get(self.endpoint)
        self._set_attributes(**result)

    def __getattr__(self, name):
        """
        lazily return attributes, only contact duedil if necessary
        """
        try:
            return super(SearchResource, self).__getattribute__(name)
        except AttributeError:
            if name in self.attribute_names:
                self.load()
                return super(SearchResource, self).__getattribute__(name)
            elif name in self.result_obj.keys():
                # Assumes subclass has dict defined called result_obj, this maps attribute name to
                # string of module path including class to be instaniated.
                # The below dynamically imports the module and then gets the class, then returns and instance of the class
                mod_path, klass_str = self.result_obj[name].rsplit('.', 1)
                mod = import_module(mod_path)
                klass = getattr(mod, klass_str)
                return klass(self.id, client=self.client, locale=self.locale, load=self.should_load)
            else:
                raise

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        return self.id == other

    def __str__(self):
        return 'Search Result: {} ({})'.format(self.name, self.id)



class SearchResouceList(Sequence):

    def __init__(self, results, result_klass, client):
        self._result_list = []
        self.result_klass = result_klass
        self.client = client
        self.result_list = results

    def __len__(self):
        return len(self.result_list)

    def __getitem__(self, key):
        return self.result_list[key]

    def __iter__(self):
        return iter(self.result_list)

    def __contains__(self, result):
        return result in self.result_list

    def __eq__(self, other):
        rlist = self.result_list == other.result_list
        client = self.client == other.client
        rclass = self.result_klass == other.result_klass
        return rlist and client and rclass

    def __add__(self, other):
        if self.client.api_key == other.client.api_key:
            return self.result_list + other.result_list
        raise TypeError('Cannot join results from 2 different applications (api keys)')

    def __radd__(self, other):
        return self.__add__(other)

    @property
    def result_list(self):
        return self._result_list

    @result_list.setter
    def result_list(self, value):
        temp = [self.result_klass(self.client, **r) for r in value.get('response',{}).get('data', {})]
        if not self._result_list:
            self._result_list = temp
        else:
            self._result_list.extend(temp)
