"""
    Query Collections

    The MIT License (MIT)

    Copyright (c) 2016 Cory Forward

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
from functools import partialmethod


class exceptions:
    class InvalidQueryException(Exception):
        pass


class query_dict(dict):
    """
    We need delattr and setattr in order to set and delete members
    in a fashion such as dict_instance.name = "cory"
    """
    __delattr__ = dict.__delattr__
    __setattr__ = dict.__setattr__

    def __getattr__(self, item):
        item = self.get(item)

        if item:
            if isinstance(item, list):
                return query_list(item)
            elif isinstance(item, dict):
                return query_dict(item)
            else:
                return item
        else:
            return None

    def query(self, query_string):
        """
        Performs a query search with 'query_string' as the search
        string
        :param query_string: Search string to access desired member(s)
        :return: object(s) if exists, otherwise exception is thrown
        """
        return search(self, query_string)


class query_list(list):
    @property
    def len(self):
        return self.__len__()

    length = partialmethod(len)

    def query(self, query_string):
        """
        Performs a query search with 'query_string' as the search
        string
        :param query_string: Search string to access desired member(s)
        :return: object(s) if exists, otherwise exception is thrown
        """
        return search(self, query_string)

    def memeq(self, value):
        pass


from query_collections.query_search import search

__all__ = (
    'query_list',
    'query_dict',
    'exceptions'
)
