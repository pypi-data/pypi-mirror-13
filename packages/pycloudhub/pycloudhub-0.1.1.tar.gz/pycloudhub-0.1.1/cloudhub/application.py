import json
import os

from bigpy import DotDict
from cloudhub.common import ensure_not_blank, CloudHubApiError, CloudHubApi


class ApplicationInfoError(CloudHubApiError):
    """
    An exception thrown in case of an issue with accessing CloudHub application information.
    """
    pass


class ApplicationNotFoundError(CloudHubApiError):
    """
    An exception thrown in case of an HTTP 404 Not Found response status code.
    """
    def __init__(self, message='Application Not Found', status_code=404):
        super(ApplicationNotFoundError, self).__init__(message, status_code)


class ApplicationDeploymentError(CloudHubApiError):
    """
    An exception thrown in case of an issue with deploying CloudHub application.
    """
    pass


class NamedApplicationApiBase(CloudHubApi):
    """
    Base class for the APIs dealing with the functionality specific to a single application
    """
    def __init__(self, user_name, password, application_name, api_base_url=None, cached_app_info=None):
        super(NamedApplicationApiBase, self).__init__(user_name, password, api_base_url)
        self.application_name = ensure_not_blank(application_name, 'Application name must not be blank')
        self.__cached_app_info = cached_app_info

    def __load_app_info(self):
        error_message='Unable to retrieve information for application [{0}]'.format(self.application_name)
        return self._load_single(error_message=error_message)

    @property
    def _base_url(self):
        return '{0}/v2/applications/{1}/'.format(self.api_base_url, self.application_name)

    @property
    def app_info(self):
        if not self.__cached_app_info:
            self.__cached_app_info = self.__load_app_info()
        return self.__cached_app_info


class ApplicationTrackingApi(NamedApplicationApiBase):

    @property
    def _base_url(self):
        return '{0}/applications/{1}/tracking'.format(self.api_base_url, self.application_name)

    def get_transaction(self, transaction_id):
        return self._load_list(
            'transactions/{0}'.format(transaction_id),
            'Unable to retrieve transaction id [{0}]'.format(transaction_id)
        )


class ApplicationLoggingApi(NamedApplicationApiBase):

    @property
    def _base_url(self):
        return self._combine_path(super(ApplicationLoggingApi, self)._base_url, 'tracking/')


class CloudHubDeployment(NamedApplicationApiBase):
    pass


class CloudHubApplication(NamedApplicationApiBase):

    LOGGING_VERSION_1 = 'VERSION_1'
    LOGGING_VERSION_2 = 'VERSION_2'
    DESC = 'DESC'
    ASC = 'ASC'

    VALID_LOGGING_VERSIONS = {LOGGING_VERSION_1, LOGGING_VERSION_2}
    VALID_ORDER_BY_DATE = {DESC, ASC}

    def find_deployments(self, order_by_date=DESC, logging_version=None):
        if order_by_date not in self.VALID_ORDER_BY_DATE:
            raise ValueError('Invalid order of deployments: [{0}]'.format(order_by_date))
        if logging_version and (logging_version not in self.VALID_LOGGING_VERSIONS):
            raise ValueError('Invalid logging version: [{0}]'.format(logging_version))

        if not logging_version:
            logging_version = self.LOGGING_VERSION_2 if self.app_info.loggingNgEnabled else self.LOGGING_VERSION_1

        params = {
            'orderByDate': order_by_date,
            'loggingVersion': logging_version
        }
        result = self._load_single('/deployments', error_message='Unable to load deployments', params=params)
        return DotDict({
            'total_count': result.total,
            'deployment_list': result.data
        })

    @property
    def tracking(self):
        return ApplicationTrackingApi(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self.__cached_app_info
        )

    @property
    def deployments(self):
        return self.find_deployments()

    def deployment_logs(self, deployment_id, limit=100, message_length=5000, tail=True):
        params = {
            'limit': limit,
            'limitMsgLen': message_length,
            'tail': tail
        }
        result = self._load_single(
                '/deployments/{0}/logs'.format(deployment_id),
                error_message='Unable to load deployments',
                params=params
        )
        return DotDict({
            'total_count': result.total,
            'log_entries': result.data
        })


class ApplicationApi(CloudHubApi):
    """
    Encapsulates the interactions with the CloudHub Application API
    """
    @property
    def _base_url(self):
        return self.api_base_url + '/applications'

    def get_applications(self):
        return self._load_list('', 'Unable to retrieve list of applications')

    def application(self, name):
        return CloudHubApplication(
            self.user_name,
            self.password,
            name,
            self.api_base_url
        )

    def get_application_info(self, name):
        response = self._get(name)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 404:
            raise ApplicationNotFoundError("Application [{0}] doesn't exist".format(name))
        else:
            code = response.status_code
            raise ApplicationInfoError(
                'Unable to retrieve information for application [{0}] (Status Code: {1})'.format(name, code),
                code
            )

    def get_application_tracking(self, name):
        return ApplicationTrackingApi(self.user_name, self.password, name, self.api_base_url)

    def deploy(self, archive_to_deploy, name=None):
        name = name if name else os.path.splitext(os.path.basename(archive_to_deploy))[0]
        app_info = self.get_application_info(name)

        payload = {
            "muleVersion": app_info["muleVersion"],
            "workers": str(app_info["workers"]),
            "workerType": app_info["workerType"]
        }

        properties = app_info["properties"]

        for prop in properties:
            payload["properties." + prop] = properties[prop]

        response = self._put(name, data=payload, files={'file': archive_to_deploy})
        if response.status_code != 200:
            raise ApplicationDeploymentError(
                "Failed to deploy application [{0}] (Status Code: {1}".format(name, response.status_code),
                response.status_code
            )


