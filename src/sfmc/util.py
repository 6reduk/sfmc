"""Helpful funcs"""

import datetime


def sobject_to_dict(obj, key_to_lower=False, json_serialize=False):
    """
    Converts a suds object to a dict.
    :param json_serialize: If set, changes date and time types to iso string.
    :param key_to_lower: If set, changes index key name to lower case.
    :param obj: suds object
    :return: dict object
    """

    if not hasattr(obj, '__keylist__'):
        if json_serialize and isinstance(obj, (datetime.datetime, datetime.time, datetime.date)):
            return obj.isoformat()
        else:
            return obj
    data = {}
    fields = obj.__keylist__
    for field in fields:
        val = getattr(obj, field)
        if key_to_lower:
            field = field.lower()
        if isinstance(val, list):
            data[field] = []
            for item in val:
                data[field].append(sobject_to_dict(item, json_serialize=json_serialize))
        else:
            data[field] = sobject_to_dict(val, json_serialize=json_serialize)
    return data


def suds_results_to_simple_types(results):
    return [sobject_to_dict(d) for d in results]


def check_required_keys(params, required, pass_empty=True):
    provided = set()

    def check_empty(f):
        if pass_empty is False and f == '':
            return False

        return True

    for key, value in params.items():
        if value is not None and check_empty(value):
            provided.add(key)

    missing = set(required) - set(provided)

    if len(missing) > 0:
        raise Exception(f"missing required keys: {missing} in {params}")


def all_keys_not_none(d: dict, required: list):
    """
    Check all values for given keys is not None
    :param d:
    :param required:
    :return:
    """
    passed = 0
    for r in required:
        v = d.get(r)
        if v is not None:
            passed += 1

    return len(required) == passed


def any_keys_not_none(d: dict, required: list):
    """
    Check although 1 element is not None but not all required
    :param d:
    :param required:
    :return:
    """
    passed = 0
    for r in required:
        v = d.get(r)
        if v is not None:
            passed += 1

    if len(required) == 1 and passed == len(required):  # Exclusion for sequence with 1 element
        return True

    return 0 < passed < len(required)
