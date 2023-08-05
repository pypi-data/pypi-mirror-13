"""
This module contains **drf-ember** exceptions and exception handlers.

The ``JsonApiException`` and the ``exception_handler`` function are
the two members of this module that you are most likely to want to understand
for modification and/or re-use.

JsonApiException
----------------

The ``JsonApiException`` is a straightforward extension of the
Django REST Framework's ``APIException``.  It's a way to raise
an exception with detail about how the JSON API specification was
broken.

exception_handler
-----------------

In the Django REST Framework, the ``exception_handler`` is a function
that allows customization of exception responses. From the DRF docs::

    You can implement custom exception handling by creating a handler
    function that converts exceptions raised in your API views into
    response objects. This allows you to control the style of error
    responses used by your API.

    The function must take a pair of arguments, this first is the
    exception to be handled, and the second is a dictionary containing
    any extra context such as the view currently being handled. The
    exception handler function should either return a ``Response`` object,
    or return ``None`` if the exception cannot be handled. If the handler
    returns ``None`` then the exception will be re-raised and Django will
    return a standard HTTP 500 'server error' response.

As would be expected, the **drf-ember** handler works to convert DRF errors into
the JSON API *error object* format.

In addition, the function also provides an important configuration option that
determines assignment of HTTP status codes.

Safe HTTP status codes
^^^^^^^^^^^^^^^^^^^^^^

Some HTTP status codes "leak" too much information that may help attackers. For example,
if a response indicated that permission is denied for a resource, it reveals its
existence.  While this might be acceptable while looking for an article on a news site,
it is unlikely to be acceptable with many other types of data handled by web applications
using this adapter. As a result, this module's ``exception_handler`` may be
configured to return *"safe"* codes and associated detail messages that are
coarse yet helpful.

When in this safe sstatus mode, all non-safe client codes default to 400.
So, for example, 403 and 404 errors raised internally are returned as 400.
All server errors are returned as the generic 500.

However, the responsibility of ensuring your client will properly handle
this change remains with you.  The JSON API specification *requires* leaky
status codes in responses.

**Safe codes**:
    - **400** Bad Request
    - **401** Unauthorized (i.e. Login)
    - **422** Unprocessable Entity (i.e. validation error)
    - **429** Too Many Requests
    - **500** Internal Server Error

Classes & functions
-------------------

The public **drf-ember** API's classes & functions.
"""
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db.models import ForeignKey, ManyToManyField, OneToOneField
from rest_framework import status
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from .utils.format import format_value


class JsonApiException(exceptions.APIException):
    """Failed to implement the expected mechanics of the JSON API"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'


def is_safe_only():
    """
    Checks for ``SAFE_CODES`` value in Django settings for ``DRF_EMBER``.

    Returns:
        bool: ``True`` if the Django settings for **drf-ember** activate safe
            status codes mode. ``False`` otherwise. See the :doc:`Settings Guide <settings>`.
    """
    safe = False
    if hasattr(settings, 'DRF_EMBER'):
        drf_ember_settings = settings.DRF_EMBER
        if 'SAFE_CODES' in drf_ember_settings:
            safe = drf_ember_settings['SAFE_CODES']
    return safe


def make_error_object(status_code='400', pointer='/data', detail='Bad request'):
    """
    Returns:
         dict: The default basic error ``dict`` has ``status`` **'400'**, a source pointer to
    **'/data'** and error detail of **'Bad request'**.
    """
    if isinstance(status_code, int):
        #JSON API requires status code must be a string
        status_code = str(status_code)
    error_object = {
        'status': status_code,
        'source': {
            'pointer': pointer
        },
        'detail': detail
    }
    return error_object


def make_generic_400_response():
    """
    Returns:
        Django REST Framework *Response*: The response's data contains a
            JSON API document where the ``errors`` member is a list with
            a single simple '400' error object created by this module's
            ``maker_error_object`` function.
    """
    error_object = make_error_object()
    data = {'errors': [error_object]}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


def to_safe_error(status_code, detail=None):
    """
    Arguments:
        status_code (int): An HTTP status code.
        detail: Error message explanatory detail.
    Returns:
        tuple: A 400 integer and "Bad request" detail message if it's not a "safe code".
            Safe codes are: 401, 422, 429, 500. Otherwise the passed status code as an integer.
    """
    candidate_code = int(status_code)
    if candidate_code in [401, 422, 429, 500]:
        return candidate_code, detail
    else:
        return 400, 'Bad request'


def get_field_type(field, model):
    """
    Arguments:
        field (str): A string name for a resource field.
        model (object): A Django model class.
    Returns:
        str: A 'relationships' string if field represents a model relationship.
        Otherwise, returns 'attributes' string.
    """
    field_type = 'attributes'
    if hasattr(model, '_meta'):
        model_meta = model._meta
        model_field_type = model_meta.get_field(field)
        if isinstance(model_field_type, (ForeignKey, ManyToManyField, OneToOneField)):
            field_type = 'relationships'
    return field_type


def convert_to_error_objects(exception_detail, status_code, model=None):
    """
    Converts a Django REST Framework (DRF) validation error dict - typically an
    exception detail - into JSON API error objects.

    Arguments:
        exception_detail (dict): In DRF, this is expected to be a dict
            keyed to field names and/or a ``non-field error`` key. The values
            are lists of string; each string is an error explanation.
            ::

                {
                    'field1': ['errorA', 'errorB'],
                    'field2': ['errorA', 'errorB'],
                    'non_field_error': ['errorX', 'errorZ']
                }

        status_code (str): An HTTP status code (e.g. 400, 422, 500)

    Returns:
        list: A list of error object dictionaries. If no error objects are created, the list
        will be empty.
    """
    error_objects = list()
    # extract non-field errors
    non_field_errors_key = api_settings.NON_FIELD_ERRORS_KEY
    if non_field_errors_key in exception_detail:
        detail_messages = exception_detail[non_field_errors_key]
        for message in detail_messages:
            error_object = make_error_object(status_code=status_code, detail=message)
            error_objects.append(error_object)
    # extract errors for each key; for model serializer errors, each key is a field's errors
    for field, detail_messages in exception_detail.items():
        for message in detail_messages:
            dasherized_field = format_value(field)
            field_type = get_field_type(field, model)
            pointer = '/data/{0}/{1}'.format(field_type, dasherized_field)
            error_object = make_error_object(status_code, pointer, message)
            error_objects.append(error_object)
    return error_objects


def add_error_objects(errors, exception_detail, status_code, model=None):
    """
    Adds Django REST Framework exception detail(s) into JSON API error
    errors list.
    """
    if isinstance(exception_detail, dict):
        error_objects = convert_to_error_objects(exception_detail, status_code, model)
        errors.extend(error_objects)
    else:
        error_object = make_error_object(status_code=status_code, detail=exception_detail)
        errors.append(error_object)


def transform_exception_detail(exception_detail, status_code, errors=None, model=None):
    """
    Handles reformatting of Django exception detail data into JSON API's error format.

    Returns:
        list: A list of JSON API error objects.
    """
    if errors is None:
        errors = list()
    if isinstance(exception_detail, list):
        details = exception_detail
        for detail in details:
            # recursion until there's no additional nested lists
            transform_exception_detail(detail, status_code, errors=errors, model=model)
    else:
        add_error_objects(errors, exception_detail, status_code, model=model)
    return errors


def is_running_test():
    """
    Checks if a testing flag on the test app is on.

    Returns
        bool: ``True`` if testing setting is set. ``False`` otherwise.
    """
    testing = False
    if hasattr(settings, 'DRF_EMBER'):
        drf_ember_settings = settings.DRF_EMBER
        if 'TESTING' in drf_ember_settings:
            testing = drf_ember_settings['TESTING']
    return testing


def exception_handler(exception, context):
    """
    To use this exception handler function, update your Django settings.
    ::

        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'drf_ember.exceptions.exception_handler'
        }

    **Safe Code Mode**

    Some HTTP status codes "leak" too much information that may help attackers.

    **drf-ember** provides you the option of using your Django app settings
    to ensure leaky codes are not returned.

    Please read the :doc:`Settings Guide <settings>` for details
    on how to activate safe code mode. If safe codes are activated,
    this handler only returns *"safe"* codes and associated detail messages
    that are coarse yet helpful. All non-safe client codes default to 400.
    So, for example, 403 and 404 errors raised internally
    are returned as 400.  All server errors are returned as the generic 500.

    Safe codes:
        - **400** Bad Request
        - **401** Unauthorized (i.e. Login)
        - **422** Unprocessable Entity (i.e. validation error)
        - **429** Too Many Requests
        - **500** Internal Server Error

    Arguments:
        exception (object): The raised exception.
        context: Context information, such as the view.

    Returns:
        DRF *Response*: The response in instantiated with a status code and
            error data; may also have headers data.
    """
    # default is a 500 error, which is what returning None triggers.
    response = None
    headers = {}
    safe_codes_on = is_safe_only()
    # This is a 422 validation error.
    if isinstance(exception, exceptions.ValidationError):
        status_code = '422'
        model = None
        if context['view']:
            model = getattr(context['view'], 'model', None)
        errors = transform_exception_detail(exception.detail, status_code, model=model)
        data = {'errors': errors}
        response = Response(data, status=422, headers=headers)
        if is_running_test():
            print('{0} Passed exception detail(s): {1}'.format('422', exception.detail))
    # 404 exception switched to 400 if safe mode on
    elif isinstance(exception, Http404):
        if safe_codes_on:
            response = make_generic_400_response()
        else:
            message_404 = 'Not found'
            errors = transform_exception_detail(message_404, '404', model=None)
            data = {'errors': errors}
            response = Response(data, status=404)
        if is_running_test():
            print('{0} Passed exception detail(s): {1}'.format('404', 'Not found'))
    # 403 exception switched to 400 if safe mode on
    elif isinstance(exception, PermissionDenied):
        if safe_codes_on:
            response = make_generic_400_response()
        else:
            message_403 = 'Permission denied'
            errors = transform_exception_detail(message_403, '403', model=None)
            data = {'errors': errors}
            response = Response(data, status=403, headers=headers)
        if is_running_test():
            print('{0} Passed exception detail(s): {1}'.format('403', 'Permission denied'))
    # 400 from this module's JSON API-focused exception
    elif isinstance(exception, JsonApiException):
        errors = transform_exception_detail(exception.detail, exception.status_code)
        data = {'errors': errors}
        if is_running_test():
            print('{0} Passed exception detail(s): {1}'.format(str(exception.status_code),
                                                               exception.detail))
        response = Response(data, status=exception.status_code)
    # Everything else
    elif isinstance(exception, exceptions.APIException):
        # handle 401 header
        if getattr(exception, 'auth_header', None):
            headers['WWW-Authenticate'] = exception.auth_header
            status_code = '401'
            exception_detail = exception.detail
        # handle 429 header
        elif getattr(exception, 'wait', None):
            headers['Retry-After'] = '%d' % exception.wait
            status_code = '429'
            exception_detail = exception.detail
        else:
            status_code = '400' if safe_codes_on else exception.status_code
            exception_detail = 'Bad request' if safe_codes_on else exception.detail
        # transform DRF error data into JSON API error format
        errors = transform_exception_detail(exception_detail, status_code)
        data = {'errors': errors}
        if is_running_test():
            print('{0} Passed exception detail(s): {1}'.format(str(exception.status_code),
                                                               exception.detail))
        response = Response(data, status=int(status_code), headers=headers)
    return response