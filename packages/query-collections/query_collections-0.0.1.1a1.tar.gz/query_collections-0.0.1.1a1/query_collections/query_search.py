import copy
from collections import deque
from enum import Enum
from . import exceptions, query_list, query_dict


class NodeType(Enum):
    BASIC_MEMBER = 0
    WILD_CARD = 1
    EXIST = 2

class QueryNode():
    node_type = None  # NodeType
    value = None

    def __init__(self, search_string):
        node_type = classify(search_string)
        if node_type is NodeType.BASIC_MEMBER:
            self.value = search_string
        elif node_type is NodeType.EXIST:
            self.value = search_string.split('!')[0]
        self.node_type = node_type


def classify(search_string):
    if search_string == "*":
        return NodeType.WILD_CARD
    elif search_string.find("!") != -1:
        return NodeType.EXIST
    else:
        return NodeType.BASIC_MEMBER


def __make_search_deque__(query_string):
    """
    Makes the search stack associated with a query string
    :param query_string: String to create stack based on
    :return: collections.deque representing the query
    """
    result = deque()
    query_components = query_string.split(":")
    for query_component in query_components:
        result.append(QueryNode(query_component))
    return result


def search(item, search_string):
    if search_string is None or search_string == '':
        raise exceptions.InvalidQueryException
    search_deque = __make_search_deque__(search_string)
    return __rec_search__(item, search_deque)


def __rec_search__(item, search_deque):
    # base case, our search deque is empty, item is what we wanted
    if not search_deque:
        if isinstance(item, list):
            return query_list(item)
        elif isinstance(item, dict):
            return query_dict(item)
        else:
            return item

    # get our query component
    query_component = search_deque.popleft()

    if query_component.node_type == NodeType.BASIC_MEMBER:
        """
        We want to continue searching, if it is the desired member it will
        reach our base case
        """
        return __rec_search__(Handlers[NodeType.BASIC_MEMBER](item, query_component), search_deque)

    elif query_component.node_type == NodeType.WILD_CARD:
        """
        We want to search each member of the current item with the search_deque
        """
        return Handlers[NodeType.WILD_CARD](item, search_deque)

    elif query_component.node_type == NodeType.EXIST:
        """
        We want to return True if the item exists, otherwise False
        """
        return Handlers[NodeType.EXIST](item, query_component, search_deque)


def handle_basic_member(component, query_component):
    """
    Handles a basic member query, assuming the item is NOT an
    object that is not a list or a map
    :param component: list or map to search
    :param query_component: QueryNode to search for
    :param silent: If we do not want to raise an exception, set silent to true
    :return: value of component if it exists, otherwise throws exception
    """
    if isinstance(component, list):
        try:
            index = int(query_component.value)
        except ValueError:
            raise IndexError("Tried to lookup a non-numeric value member %s in a list!" % query_component.value)

        return component[index]
    elif isinstance(component, dict):
        handle_item = component.get(query_component.value)

        if handle_item is not None:
            return handle_item
        else:
            raise KeyError("Member with name %s was not found!" % query_component.value)
    else:
        raise SyntaxError(
            "Attempted to perform a query on member %s which was not a map or a list!" % query_component.value)


def handle_wildcard(component, search_deque):
    """
    If we receive a wildcard we want
    :param component: object to search through
    :param search_deque: search deque to perform search with
    :return:
    """
    results = []
    item_list = None  # for clarity purposes

    if isinstance(component, list):
        """
        If we are a list, we want to perform the search on
        each item of the inputted component and return the
        matches
        """
        item_list = component

    elif isinstance(component, dict):
        """
        If we are a map, we want to perform the search on
        each value in our key,value map and return the matches
        """
        item_list = component.values()
    else:
        if search_deque:
            raise SyntaxError(
                "Attempted to search for member %s, but the parent was not a dict or a list!" % search_deque.popleft().value)
        else:
            """
            If we do not have a search deque, this item is the wildcard
            member of the parent component, and is what was wanted.
            (e.g.: dict_instance.query("*") returns the dict_instance)
            """
            return component

    for item in item_list:
        try:
            result = __rec_search__(item, copy.copy(search_deque))
            results.append(result)
        except:
            """
            If the item did not have a query matching value,
            skip it.
            """
            continue

    return results


def exists(component, query_component):
    try:
        handle_basic_member(component, query_component)
        return True
    except:
        return False


def handle_exist(component, query_component, search_deque):
    if search_deque:
        if exists(component, query_component):
            return __rec_search__(component, search_deque)
        else:
            raise Exception("Attempted to search for a value after %s, but %s did not exist" % (query_component.value,query_component.value))
    else:
        return exists(component, query_component)


Handlers = {
    NodeType.BASIC_MEMBER: handle_basic_member,
    NodeType.WILD_CARD: handle_wildcard,
    NodeType.EXIST: handle_exist
}
