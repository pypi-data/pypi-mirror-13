import os

# Set sane default to '' so that application does not break
# Set in values in /etc/environment or ~/.pam_environment
APPLICATION_ID = os.environ.get('PARSE_APPLICATION_ID', '')
REST_API_KEY = os.environ.get('PARSE_REST_API_KEY', '')

API_URL = os.environ.get('PARSE_API_URL', 'https://api.parse.com')
API_VERSION = os.environ.get('PARSE_API_VERSION', '1')
