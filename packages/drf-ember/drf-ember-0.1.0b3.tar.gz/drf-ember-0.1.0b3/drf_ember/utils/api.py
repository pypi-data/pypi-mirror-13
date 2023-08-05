"""
Utility API functions. These functions focus on transforming conventional Django REST Framework
data into JSON API formats and vice versa.
"""
import re
import inflection
from rest_framework import serializers
from rest_framework.compat import OrderedDict
from rest_framework.exceptions import MethodNotAllowed
from ..helpers import IncludedHelper
from ..exceptions import JsonApiException
from .format import format_keys, format_resource, to_dasherized_plural, format_value


def assemble_resource_identifier(resource_type, primary_key):
    """
    Arguments:
        resource_type (str): Typically, this is a pluralized model name, such as "teams".

        primary_key: The resources primary key.  The JSON API requires this be returned
         as a string.

    Returns:
        dict | ``None``: A JSON API resource identifier keyed with ``id`` and ``type``
            if a primary key is passed. ``None`` otherwise.
    """
    return {'id': str(primary_key), 'type': resource_type} if primary_key else None


def is_errors_view(view):
    """
    Supports ``render`` function calls in determining whether an API view
    is an error payload, as opposed to a *primary data* one.

    Arguments:
        view (object): A view, such as the Django REST Framework's generic View classes.

    Returns:
        bool: ``True`` if status code starts with a '4' or '5'. ``False`` otherwise.
    """
    try:
        http_status_code = str(view.response.status_code)
    except (AttributeError, ValueError):
        pass
    else:
        if http_status_code.startswith('4') or http_status_code.startswith('5'):
            return True
    return False


def is_unpaginated_list_view(data):
    """
    Supports ``render`` function calls in determining whether an API view
    data payload is an unpaginated list of resources.

    The function relies on the default approach the Django REST Framework takes
    to pagination. The function checks for the absence of framework's
    default approach of creating a wrapping object with meta data paired
    with a ``results`` key.

    Arguments:
        data (dict or list): Typically, the model data the view responds with.

    Returns:
        ``True`` if it is a unpaginated list view. ``False`` otherwise.
    """
    if 'results' not in data and isinstance(data, list):
        return True
    else:
        return False


def is_paginated_list_view(data):
    """
    Supports ``render`` function calls in determining whether an API view
    data payload is a paginated list of resources.

    The function relies on the default approach the Django REST Framework takes
    to pagination, specifically, how the framework creates a wrapping object
    with resource data keyed to ``results`` and pagination/navigation
    metadata keyed to ``count``, ``next``, and ``previous``. As a second option,
    it also checks for the presence of a ``meta`` key, such as that generated
    by the **drf-ember** pagination class.

    Arguments:
        data (dict or list): Typically, the model data the view responds with.

    Returns:
        bool: ``True`` if it is a paginated list view. ``False`` otherwise, including a list without
        pagination metadata.
    """
    if 'results' in data and 'count' in data and 'next' in data \
            and 'previous' in data and isinstance(data, dict):
        return True
    elif 'results' in data and 'meta' in data and isinstance(data, dict):
        return True
    else:
        return False


def is_single_resource_view(view, data):
    """
    Supports ``render`` function calls in determining whether an API view
    data payload is for a single resource (e.g. a 'detail' view).

    Arguments:
        view (object): A view, such as Django REST Framwork's generic View classes.
        data (dict or list): Typically, the model data the view responds with.

    Returns:
        bool: ``True`` if it is a single resource view. ``False`` otherwise.
    """
    if isinstance(data, dict) and 'results' not in data:
        return True
    else:
        return False


def get_related_resource_type(relation_field):
    """
    Returns a plural type for the relation field or an `InvalidDocumentError`
    if no model name for the field can be found.
    """
    queryset = relation_field.queryset
    if queryset is not None:
        relation_model = queryset.model
    else:
        # Handles ManyRelated (typically, a PrimaryKeyRelatedField with many=True kwarg)
        parent_serializer = relation_field.parent
        if hasattr(parent_serializer, 'Meta'):
            parent_model = parent_serializer.Meta.model
        else:
            parent_model = parent_serializer.parent.Meta.model
        parent_model_relation = getattr(
            parent_model,
            (relation_field.source if relation_field.source else parent_serializer.field_name)
        )
        if hasattr(parent_model_relation, 'related'):
            relation_model = parent_model_relation.related.model
        elif hasattr(parent_model_relation, 'field'):
            relation_model = parent_model_relation.field.related.model
        else:
            raise JsonApiException('Unable to set resource type. Can not '
                                   'find related model for relation {relation}'.format(relation=relation_field))
    return to_dasherized_plural(relation_model.__name__)


def get_resource_name(context):
    """
    Return the name of a resource from a context.
    """
    view = context.get('view')

    # Ensure we have a view.
    if not view:
        raise JsonApiException('Could not find view.')

    # Check to see if there is a status code and return early
    # with the resource_name value of `errors`.
    try:
        code = str(view.response.status_code)
    except (AttributeError, ValueError):
        pass
    else:
        if code.startswith('4') or code.startswith('5'):
            return 'errors'

    try:
        resource_name = getattr(view, 'resource_name')
    except AttributeError:
        try:
            # Check the meta class
            resource_name = (getattr(view, 'serializer_class').Meta.resource_name)
        except AttributeError:
            # Use the model
            try:
                resource_name = (getattr(view, 'serializer_class').Meta.model.__name__)
            except AttributeError:
                try:
                    resource_name = view.model.__name__
                except AttributeError:
                    resource_name = view.__class__.__name__
            # if the name was calculated automatically then pluralize and format
            resource_name = inflection.pluralize(resource_name.lower())
            resource_name = format_value(resource_name)
    return resource_name


def get_serializer_resource_type(serializer):
    """
    Returns dasherized and plural string from serializer's model.
    """
    if hasattr(serializer, 'Meta'):
        model = serializer.Meta.model
        return to_dasherized_plural(model.__name__)
    else:
        raise JsonApiException('Unable to set resource type. Can not '
                               'find model for serializer {0}'.format(serializer))


def extract_model_attributes(model_natives):
    """
    Converts model data into dict of attributes that excludes model's
    ``type`` and ``id`` attributes.

    Arguments:
        model_natives (dict): A dict of model/resource properties and associated values.

    Returns:
        dict: A dict that excludes ``type`` and ``id`` attributes from passed in dict.
    """
    attributes = {}
    model_natives.pop('id')
    model_natives.pop('type')
    for field, data in model_natives.items():
        attributes[field] = data
    return attributes


def assemble_resource_object(representation, serializer, included_helper):
    """
    Handles preparation a JSON API resource object.

    Per JSON API expectations, field keys are dasherized.

    Arguments:
        representation (dict): The data for the resource object instance.

        serializer (object): Expects a Django REST Framework Serializer class object.

        included_helper (object): A helper object that holds resource data to build the
            top-level ``included`` member.

    Returns:
        OrderedDict: A JSON API resource object
    """
    attributes = {}
    relationships = {}
    # Note use of Py3 items()
    for field_name, field_data in representation.items():
        if isinstance(serializer.fields[field_name], serializers.PrimaryKeyRelatedField):
            resource_type = get_related_resource_type(serializer.fields[field_name])
            resource_identifier = assemble_resource_identifier(resource_type, field_data)
            relationships[field_name] = {'data': resource_identifier}
            continue
        elif isinstance(serializer.fields[field_name], serializers.ManyRelatedField):
            resource_type = get_related_resource_type(serializer.fields[field_name].child_relation)
            resource_identifiers = list()
            for primary_key in field_data:
                resource_identifier = assemble_resource_identifier(resource_type, primary_key)
                resource_identifiers.append(resource_identifier)
            relationships[field_name] = {'data': resource_identifiers}
            continue
        elif isinstance(serializer.fields[field_name], serializers.ListSerializer):
            resource_identifiers = list()
            child_serializer = serializer.fields[field_name].child
            for model in field_data:
                resource_object = assemble_resource_object(model, child_serializer, included_helper)
                included_helper.add_resource(resource_object)
                resource_identifier = {'id': resource_object['id'], 'type': resource_object['type']}
                resource_identifiers.append(resource_identifier)
            relationships[field_name] = {'data': resource_identifiers}
            continue
        elif isinstance(serializer.fields[field_name], serializers.ModelSerializer):
            model_serializer = serializer.fields[field_name]
            resource_object = assemble_resource_object(field_data, model_serializer, included_helper)
            included_helper.add_resource(resource_object)
            resource_identifier = {'id': resource_object['id'], 'type': resource_object['type']}
            relationships[field_name] = {'data': resource_identifier}
            continue
        else:
            attributes[field_name] = field_data
    type_name = get_serializer_resource_type(serializer)
    resource_members = [
        ('id', str(attributes.pop('id'))),
        ('type', type_name),
        ('attributes', attributes),
    ]
    if relationships:
        resource_members.append(('relationships', relationships))
    resource = OrderedDict(resource_members)
    return format_resource(resource)


def parse_attributes(primary_data):
    """
    Parses primary data into conventional Django REST Framework format model data
    by re-formatting keys into underscored from JSON API's dasherized format.

    Arguments:
        primary_data (dict): The JSON API documents primary data.

    Returns:
        dict: The the members of the primary data's ``attributes`` field, re-keyed
         to underscore format.
    """
    attributes = None
    if 'attributes' in primary_data:
        attributes = format_keys(primary_data.get('attributes'), 'underscore')
    return attributes


def parse_resource_linkage(parsed_relationships, relationship_name, resource_linkage):
    """
    According to the JSON API specification, resource linkage MUST be
    represented as one of the following:

        - null for empty to-one relationships.
        - an empty array ([]) for empty to-many relationships.
        - a single resource identifier object for non-empty to-one relationships.
        - an array of resource identifier objects for non-empty to-many relationships.

    Arguments:
        parsed_relationships (dict): The target dict for parsed relationships output.

        relationship_name (str): The string name of the relationship field.

        resource_linkage: The candidate data for parsing.  May be ``None``, a list, or a dict
    """
    if isinstance(resource_linkage, dict):
        resource_id = resource_linkage.get('id')
        if resource_id:
            parsed_relationships[relationship_name] = resource_id
    elif isinstance(resource_linkage, list):
        primary_keys = list()
        for resource_identifier in resource_linkage:
            resource_id = resource_identifier.get('id')
            if resource_id:
                primary_keys.append(resource_id)
        parsed_relationships[relationship_name] = primary_keys
    else:
        parsed_relationships[relationship_name] = None


def parse_relationships(primary_data):
    """
    Parses ``relationships`` member of a JSON API document's primary data.

    Arguments:
        primary_data (dict): Typically keyed to model/resource fields that aren't foreign keys
            for a relationship. The value data are valid JSON values converted to built-in python types.

    Returns:
        A dict keyed to field names and their associated values if relationship data
            is present. Otherwise, returns ``None``.
    """
    if 'relationships' in primary_data:
        parsed_relationships = dict()
        relationships = format_keys(primary_data.get('relationships'), 'underscore')
        for relationship_name, relationship_object in relationships.items():
            if isinstance(relationship_object, dict):
                resource_linkage = relationship_object.get('data')
                parse_resource_linkage(parsed_relationships, relationship_name, resource_linkage)
            else:
                raise JsonApiException('Relationship object not properly implemented for '
                                       '{0} relationship'.format(relationship_name))
        return parsed_relationships
    else:
        return None


def parse_resource_object(primary_data, parser_context):
    """
    Parses a request's resource object by transforming the
    formatting of the primary data's ``attributes`` and
    ``relationships`` members.

    Arguments:
        primary_data (dict): The JSON API documents primary data

        parser_context (dict): Information about the context the view is
            being called from. Of particular importance within the logic
            of this function is the parser's request as it is inspected
            to determine the HTTP method. DRF default contains
            following keys: ``view``, ``request``, ``args``, ``kwargs``.

    Returns:
        dict: A JSON API resource object
    """
    request = parser_context.get('request')
    http_method = request.method.lower()
    if http_method in ('post', 'patch', 'delete'):
        resource = dict()
        if http_method != 'post':
            try:
                resource['id'] = primary_data['id']
            except KeyError:
                raise JsonApiException('Resource id missing')
        attributes = parse_attributes(primary_data)
        if attributes:
            resource.update(attributes)
        relationships = parse_relationships(primary_data)
        if relationships:
            resource.update(relationships)
        return resource
    else:
        raise MethodNotAllowed


def parse_bulk_resource_objects(primary_data, parser_context):
    """
    The JSON API extension for bulk creation recommends sending a POST of a list
    of resource objects with at least a ``type`` member.  The recommendation for
    an update bulk operation is a PATCH request with a list of resource objects
    with at least ``type`` and ``id`` members.

    Arguments:
        primary_data (list): A list of resource objects.
        parser_context (dict): The parser context. The DRF default includes the
            following keys: ``view``, ``request``, ``args``, ``kwargs``.

    Returns:
        A list of dicts representing the passed resources in native python types.
    """
    resources = list()
    for resource_object in primary_data:
        resource = parse_resource_object(resource_object, parser_context)
        resources.append(resource)
    return resources


def extract_page_digits(content):
    """
    Extract the page number from a Django Rest Framework pagination link.
    """
    if content:
        pattern = r'page=(\d+)'
        page_num_regex = re.compile(pattern)
        match = page_num_regex.search(content)
        if match:
            return int(match.group(1))
    return None


def list_to_jsonapi_document(data, paginated=True):
    """
    Transforms a list of models into a JSON API-formatted dictionary.

    If a 'meta' member is already present in the data, it gets transferred without
    transformation to the returned OrderedDict. This is the expected progression if
    a **drf-ember** pagination class is used.

    However, if there's no ``meta`` member AND ``count``, ``next``, and ``previous`` members are
    present, they are transformed into a ``meta`` object.  As part of the transformation, the
    ``next`` and ``previous`` values are scanned with a regular expression so that only
    page digits (and not a web link) are returned as the value for 'next' and 'previous'. This
    is the expected handling if a **drf-ember** pagination class is *not* used and instead,
    something like the DRF *PageNumberPagination* class is set.

    Arguments:
        data (dict or list): The response data. Could be a paginated dictionary or a list of models.

        paginated (boolean): If the object follows pagination conventions of
            Django Rest Framework; if it does, then there's a 'results' key paired with the primary
            data containing resource information.

    Returns:
        OrderedDict: The OrderedDict ``data`` member is a list with resource primary data;
            may contain ``meta`` and ``included`` members.
    """
    if paginated:
        # By default, DRF places primary data uner the 'results' key during pagination
        representations = data['results']
    else:
        representations = data
    resource_objects = list()
    included_helper = None
    if hasattr(representations, 'serializer'):
        # Expects a DRF ReturnList for model representations
        serializer = representations.serializer.child
        # Handling creation of a top-level 'data' JSON API document

        included_helper = IncludedHelper()
        for representation in representations:
            resource_object = assemble_resource_object(representation, serializer, included_helper)
            resource_objects.append(resource_object)
    else:
        # Not a serialized model, so the developer is responsible for providing
        # JSON API compliant dictionaries
        resource_objects = representations
    document_members = [
        ('data', resource_objects)
    ]
    if 'meta' in data:
        document_members.append(('meta', data['meta']))
    # Handles conventional DRF PageNumberPagination class
    elif 'count' in data and 'next' in data and 'previous' in data:
        meta = OrderedDict([
            ('count', data['count']),
            ('next', extract_page_digits(data['next'])),
            ('previous', extract_page_digits(data['previous']))
        ])
        document_members.append(('meta', meta))
    if included_helper and not included_helper.empty:
        document_members.append(('included', included_helper.get_included()))
    return OrderedDict(document_members)


def resource_to_jsonapi_document(data):
    """
    Checks for presence of a serializer in order to transform passed
    data into a JSON API document.

    Arguments:
        data: The data for a resource.

    Returns:
        An ``OrderedDict`` if a serializer is is present. Otherwise, returns
        the passed data without modification.
    """
    if hasattr(data, 'serializer'):
        serializer = data.serializer
        included_helper = IncludedHelper()
        resource_object = assemble_resource_object(data, serializer, included_helper)
        document_members = [
            ('data', resource_object)
        ]
        if not included_helper.empty:
            document_members.append(('included', included_helper.get_included()))
        return OrderedDict(document_members)
    else:
        # Not a serialized model, so the developer is responsible for providing
        # JSON API compliant dictionaries
        return data


