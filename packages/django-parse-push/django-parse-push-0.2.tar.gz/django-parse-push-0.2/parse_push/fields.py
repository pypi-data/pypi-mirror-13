from rest_framework import fields
from rest_framework import serializers


class EnumChoiceField(fields.Field):

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        super(EnumChoiceField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        """ Return the serialized representation. """
        inverted_dict = {v: k for k, v in self.enum.get_as_dict().iteritems()}
        return inverted_dict[value]

    def to_internal_value(self, value):
        """ Return the python based (non-serialized) value """
        keys = self.enum.get_keys()
        if not value in keys:
            msg = "Invalid kind ({}) passed. Must be one of {}!"
            raise serializers.ValidationError(msg.format(value, ', '.join(sorted(keys))))
        internal_value = self.enum.get_as_dict()[value]
        return internal_value
