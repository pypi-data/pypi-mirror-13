from rest_framework import serializers

from parse_push.enums import DeviceKind
from parse_push.fields import EnumChoiceField
from parse_push.models import Device


class DeviceSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=20, max_length=100)
    kind = EnumChoiceField(enum=DeviceKind)

    def create(self, validated_data):
        return Device.objects.create(**validated_data)
