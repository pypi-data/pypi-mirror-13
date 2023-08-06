from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import DeviceSerializer
from .models import Device


class DeviceTokenSetter(APIView):
    """
    Set a push token related to device for logged in User
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save(user=request.user)
                return Response(status=status.HTTP_200_OK)
            except IntegrityError:

                return Response('Device instance already exists.', status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            device = get_object_or_404(Device, user=request.user, token=serializer.data['token'])
            device.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
