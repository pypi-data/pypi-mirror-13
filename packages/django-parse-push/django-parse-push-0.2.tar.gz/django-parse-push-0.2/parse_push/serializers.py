from rest_framework import serializers

from parse_push.enums import DeviceKind
from parse_push.fields import EnumChoiceField
from parse_push.models import Device


class DeviceSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=20, max_length=100)
    kind = EnumChoiceField(enum=DeviceKind)

    def create(self, validated_data):
        device, created = Device.objects.get_or_create(
            token=validated_data['token'],
            defaults={
                'user': validated_data['user'],
                'kind': validated_data['kind']
            }
        )
        if not created:
            # Support switching user on a device, and also marks this
            # device as the latest one used.
            device.user = validated_data['user']
            device.save()
        return device
