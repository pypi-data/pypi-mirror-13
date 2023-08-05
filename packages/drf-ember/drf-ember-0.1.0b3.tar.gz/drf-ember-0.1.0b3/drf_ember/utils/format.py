"""Utility formatting functions.  These functions simplify string reformatting logic
common to manipulation of names and keys to switch back and forth between Django REST
Framework and Ember Data's JSON API implementation."""
import inflection
from rest_framework.compat import OrderedDict


def to_dasherized_plural(name):
    """
    Pluralizes a name, as well as transforming camelCase
    name into dasherized formatting
    """
    plural = inflection.pluralize(name)
    underscore = inflection.underscore(plural)
    dasherized = inflection.dasherize(underscore)
    return dasherized


def format_value(value, format_type='dasherize'):
    """
    Alter the format of a string value.  This is useful in
    ensuring that the keys representing serialized model field names
    are in the proper format.
    """
    if format_type == 'dasherize':
        # 2 steps because inflection library does not
        # directly dasherize camelCase
        value = inflection.underscore(value)
        value = inflection.dasherize(value)
    elif format_type == 'camelize':
        value = inflection.camelize(value, False)
    elif format_type == 'capitalize':
        value = inflection.camelize(value)
    elif format_type == 'underscore':
        value = inflection.underscore(value)
    return value


def format_keys(obj, format_type='dasherize'):
    """
    Passed dict/list gets its keys transformed. The default target format is
    dasherize, as this matches the Ember framework's JSON API conventions.
    """
    if isinstance(obj, dict):
        formatted = OrderedDict()
        for key, value in obj.items():
            if format_type == 'dasherize':
                formatted[inflection.dasherize(key)] = value
            elif format_type == 'camelize':
                formatted[inflection.camelize(key, False)] = value
            elif format_type == 'underscore':
                formatted[inflection.underscore(key)] = value
        return formatted
    if isinstance(obj, list):
        return [format_keys(item, format_type) for item in obj]
    else:
        return obj


def format_resource(obj, format_type='dasherize'):
    """
    Passed dict/list gets its keys and values transformed to a new formats.
    The default is dasherize, as this matches the Ember framework's
    JSON API conventions.
    """
    if isinstance(obj, dict):
        formatted = OrderedDict()
        for key, value in obj.items():
            if format_type == 'dasherize':
                formatted[inflection.dasherize(key)] = format_keys(value, format_type)
            elif format_type == 'camelize':
                formatted[inflection.camelize(key, False)] = format_keys(value, format_type)
            elif format_type == 'underscore':
                formatted[inflection.underscore(key)] = format_keys(value, format_type)
        return formatted
    if isinstance(obj, list):
        return [format_keys(item, format_type) for item in obj]
    else:
        return obj