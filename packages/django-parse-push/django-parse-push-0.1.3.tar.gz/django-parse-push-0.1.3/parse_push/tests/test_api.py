from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from rest_framework import status

from ..views import DeviceTokenSetter


class APITest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='donaldduck', password='topsecret')
        self.payloads = {
            'ios': {
                'token': 'iosdevicetokenabcdefghijklmnopqstuvwxyz0123456789',
                'kind': 'IOS'
            },
            'android': {
                'token': 'androiddevicetokenabcdefghijklmnopqstuvwxyz0123456789',
                'kind': 'ANDROID'
            },
            'invalid_ios': {
                'token': 'androiddevicetokenabcdefghijklmnopqstuvwxyz0123456789',
                'kind': 0
            }
        }

    def get_prepared_request(self, url='/', auth=True, payload=None):
        # Default payload is 'ios'
        payload = payload if payload in self.payloads.keys() else 'ios'
        # Create an instance of a POST request.
        request = self.factory.post(url, self.payloads[payload])
        # Disable CSRF checks
        request._dont_enforce_csrf_checks = True
        # Either logged in User or AnonymousUser
        request.user = self.user if auth else AnonymousUser()
        return request

    def test_anonymous_post(self):
        request = self.get_prepared_request(auth=False)
        response = DeviceTokenSetter.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post(self):
        # Create an instance of a POST request.
        request = self.get_prepared_request(auth=True, payload='ios')
        # Use this syntax for class-based views.
        response = DeviceTokenSetter.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_post(self):
        # NOTE: This does not work on SQLite as SQLite does not support 'unique_together'
        # Create an instance of a POST request.
        request = self.get_prepared_request(auth=True, payload='ios')
        # Use this syntax for class-based views.
        response = DeviceTokenSetter.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_ios_post(self):
        # Create an instance of a GET request.
        request = self.get_prepared_request(auth=True, payload='invalid_ios')
        response = DeviceTokenSetter.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
