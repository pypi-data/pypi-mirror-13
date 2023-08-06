import query_collections.search


class query_dict(dict):
    """
    A dictitonary implementation that has the following attributes:
        - query is directly implemented within object
        - dictionary values can be accessed with the dot operator
        via query_dict_instance.key -> returns the value associated with 'key'
    """

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
        return query_collections.search.query(self, query_string)


class query_list(list):
    """
    A list implementation that has the following attributes:
        - query is directly implemented within the object
        - the length of the list can be accessed via list_instance.len as a property
            instead of needing to invoke __length__
    """

    @property
    def len(self):
        return self.__len__()

    def query(self, query_string):
        """
        Performs a query search with 'query_string' as the search
        string
        :param query_string: Search string to access desired member(s)
        :return: object(s) if exists, otherwise exception is thrown
        """
        return query_collections.search.query(self, query_string)