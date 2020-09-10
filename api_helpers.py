import json
from flask import abort, request


def to_pretty_json(value):
    return json.dumps(value, sort_keys=False,
                      indent=4, separators=(',', ': '), ensure_ascii=False)


def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(404)
    # make response
    navigation = {'start': start, 'limit': limit, 'count': count}
    # make URLs
    # make previous url
    if start == 1:
        navigation['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        navigation['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        navigation['next'] = ''
    else:
        start_copy = start + limit
        navigation['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    navigation['Cities'] = results[start - 1:start - 1 + limit]
    return navigation


def filter_not_found(cities_list):
    if list(cities_list[0].keys())[0] == 'Search failed':
        cities_not_found = cities_list[0]
        try:
            cities_found = cities_list[1]
        except:
            cities_found = None
        return cities_not_found, cities_found, None
    else:
        cities_not_found = None
        cities_found = cities_list[0]
        try:
            cities_comparison = cities_list[1]
            return cities_not_found, cities_found, cities_comparison
        except:
            return cities_not_found, cities_found, None