"""
Classes and functions used throughout the package
"""
import requests
from bigpy import ensure_not_blank, trim, DotDict


class CloudHubError(Exception):
    """
    Base exception class for different exceptions raised in this package.
    """
    pass


class CloudHubApiError(CloudHubError):
    """
    Root of the exception hierarchy for communicating errors when interacting with CloudHub API.
    It carries the HTTP status code along with the message.
    """
    def __init__(self, message, status_code):
        super(CloudHubApiError, self).__init__(message)
        self.status_code = status_code


class CloudHubUnauthorizedError(CloudHubApiError):
    """
    Raised in response to HTTP status 401
    """
    DEFAULT_MESSAGE = 'Unauthorized: Access is denied due to invalid credentials'

    def __init__(self, message=DEFAULT_MESSAGE, status_code=401):
        super(CloudHubUnauthorizedError, self).__init__(message, status_code)


class CloudHubApi(object):
    """
    Base class for all components interacting with the CloudHub API
    """
    API_BASE_URL = 'https://anypoint.mulesoft.com/cloudhub/api'

    def __init__(self, user_name, password, api_base_url=None):
        """
        Initializes API handler class with the credentials and optional base URL to use. If no explicit base URL
        is specified, a default URL will be used.

        :param user_name: the user name to access CloudHub
        :param password: the password to access CloudHub
        :param api_base_url: the base URL to use for the API calls.
        """
        self.user_name = ensure_not_blank(user_name, 'The user name must not be blank')
        self.password = ensure_not_blank(password, 'The password must not be blank')

        api_base_url = trim(api_base_url)
        self.api_base_url = api_base_url if api_base_url else CloudHubApi.API_BASE_URL

        # remove trailing '/'
        self.api_base_url = self.api_base_url.strip('/')

    @staticmethod
    def _combine_path(base_url, path):
        base_url = trim(base_url).strip('/')
        path = trim(path).strip('/')
        return '{0}/{1}'.format(base_url, path) if path else base_url

    @staticmethod
    def _extract_error_description(response, default_message=None):
        try:
            parsed = response.json()
            if 'message' in parsed and parsed['message']:
                return parsed['message']
        except ValueError:
            return default_message if default_message else 'Unknown error occurred'

    @staticmethod
    def _handle_standard_errors(response, default_message=None):
        if response.status_code == 401:
            raise CloudHubUnauthorizedError()
        else:
            message = '{0} (Status code: {1})'.format(
                CloudHubApi._extract_error_description(response, default_message),
                response.status_code
            )
            raise CloudHubApiError(message, response.status_code)

    @staticmethod
    def _init_headers(headers=None, has_content=False):
        headers = dict(headers) if headers else {}
        headers['Accept'] = 'application/json'
        if has_content:
            headers['Content-Type'] = 'application/json'
        return headers

    @property
    def _base_url(self):
        return self.api_base_url

    def _make_url(self, path):
        return self._combine_path(self._base_url, path)

    def _get(self, path=None, params=None, headers=None):
        headers = self._init_headers(headers, has_content=True)
        return requests.get(
                self._make_url(path),
                auth=(self.user_name, self.password),
                params=params,
                headers=headers
        )

    def _put(self, data, path=None, headers=None, **kwargs):
        headers = self._init_headers(headers, has_content=True)
        return requests.put(
                self._make_url(path),
                auth=(self.user_name, self.password),
                headers=headers,
                data=data,
                **kwargs
        )

    def _post(self, data, path=None, headers=None, **kwargs):
        headers = self._init_headers(headers, has_content=True)
        return requests.post(
                self._make_url(path),
                auth=(self.user_name, self.password),
                headers=headers,
                data=data,
                **kwargs
        )

    def _load_single(self, path=None, error_message=None, params=None):
        response = self._get(path, params)
        if response.status_code == 200:
            return DotDict(response.json())
        else:
            self._handle_standard_errors(response, error_message)

    def _load_list(self, path, error_message=None):
        response = self._get(path)
        if response.status_code == 200:
            return [DotDict(x) for x in response.json()]
        else:
            self._handle_standard_errors(response, error_message)
