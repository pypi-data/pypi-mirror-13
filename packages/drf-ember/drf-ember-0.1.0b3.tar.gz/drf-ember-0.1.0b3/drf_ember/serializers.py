"""
Serializer mixin and class for handling bulk requests.
"""
import inspect
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ListSerializer, ModelSerializer


class BulkSerializerMixin(object):
    """
    For PATCH requests, restores the resource identifier (i.e. primary key) based on
    the ``update_lookup_field`` into validated data.  The
    default logic of the ``Serializer`` class' ``to_internal_value`` method
    strips out read-only fields; this includes typical `id` primary key field,
    and therefore needs this mixin's override for restoration.
    """

    def to_internal_value(self, data):
        """
        Restores lookup field for PATCH requests for the resource/model's internal value.

        For PATCH requests, this method implementation overrides ``Serializer`` class's
        ``to_internal_value`` method default stripping out of read-only ``id`` field.

        Arguments:
            data (dict): A dict of primitive data types

        Returns:
            If valid, an ``OrderedDict`` of native values, such as Django model objects
            and datetime objects.  ``ValidationError`` otherwise.
        """
        internal_value = super(BulkSerializerMixin, self).to_internal_value(data)
        id_attr = getattr(self.Meta, 'bulk_lookup_field', 'id')
        request_method = getattr(getattr(self.context.get('view'), 'request'), 'method', '')
        if all((isinstance(self.root, BulkListSerializer),
                id_attr,
                request_method in ('PATCH', 'patch'))):
            id_field = self.fields[id_attr]
            id_value = id_field.get_value(data)
            internal_value[id_attr] = id_value
        return internal_value


class BulkListSerializer(ListSerializer):
    """
    Provides update logic to improve efficiency for updates to a list of persisted models.
    """

    def update(self, queryset, all_validated_data):
        """
        Bulk update method for list serializer.

        Remember, this logic is called when a serializer was passed instance
        *and* new data when initialized. Therefore, it's not a create save
        operation but an update one.
        """
        id_attr = getattr(self.child.Meta, 'bulk_lookup_field', 'id')
        # reformat to dict { '1': data1, '2': data2, etc. } for filtering
        validated_objects = {
            data.pop(id_attr): data for data in all_validated_data
        }
        key_checks = [bool(key) for key in validated_objects.keys()]
        if not all(key_checks):
            raise ValidationError('Invalid primary key within bulk update request')
        # filter passed query set for models from validated data
        filter_kwarg = {
            '{}__in'.format(id_attr): validated_objects.keys(),
        }
        target_objects = queryset.filter(**filter_kwarg)
        if len(validated_objects) != target_objects.count():
            raise ValidationError('Resources in update request do not exist in database')
        updated_objects = list()
        for target_object in target_objects:
            object_id = getattr(target_object, id_attr)
            obj_validated_data = validated_objects.get(object_id)
            # use model serializer to actually update the model
            # in case that method is overwritten
            updated_objects.append(self.child.update(target_object, obj_validated_data))
        return updated_objects
