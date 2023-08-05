"""
Implements the CloudHub API functionality related to the single application.
"""
import datetime
import json

from bigpy import DotDict

from cloudhub.common import ensure_not_blank, CloudHubApiError, CloudHubApi, datetime_to_cloudhub_format


class ApplicationDeploymentError(CloudHubApiError):
    """
    An exception thrown in case of an issue with deploying CloudHub application.
    """
    pass


class ApplicationBase(CloudHubApi):
    """
    Base class for the APIs dealing with the functionality specific to a single application
    """
    def __init__(self, user_name, password, application_name, api_base_url=None, cached_app_info=None):
        super(ApplicationBase, self).__init__(user_name, password, api_base_url)
        self.application_name = ensure_not_blank(application_name, 'Application name must not be blank')
        self.__cached_app_info = cached_app_info

    def __load_app_info(self):
        error_message = 'Unable to retrieve information for application [{0}]'.format(self.application_name)
        return self._load_single(error_message=error_message)

    @property
    def _base_url(self):
        return '{0}/v2/applications/{1}/'.format(self.api_base_url, self.application_name)

    @property
    def app_info(self):
        if not self.__cached_app_info:
            self.__cached_app_info = self.__load_app_info()
        return self.__cached_app_info


class SearchParameter(object):
    """
    Represents CloudHub transactions search parameter.
    """
    def __init__(self, name, value, operator):
        self.name = ensure_not_blank(name, 'The search parameter name must not be blank')
        self.value = ensure_not_blank(value, 'The search parameter value must not be blank')
        self.operator = ensure_not_blank(operator, 'The search parameter operator must not be blank')

    def to_dict(self):
        return DotDict({
            'name': self.name,
            'value': self.value,
            'operator': self.operator
        })

    @staticmethod
    def transaction_id(value, operator):
        return SearchParameter('transactionId', value, operator)

    @staticmethod
    def flow_name(value, operator):
        return SearchParameter('flowName', value, operator)

    @staticmethod
    def exception_message(value, operator):
        return SearchParameter('exceptionMessage', value, operator)

    @staticmethod
    def processing_time(value, operator):
        return SearchParameter('processingTime', value, operator)


class CloudHubApplicationTracker(ApplicationBase):

    @property
    def _base_url(self):
        return '{0}/applications/{1}/tracking'.format(self.api_base_url, self.application_name)

    def transaction(self, transaction_id):
        return self._load_list(
            'transactions/{0}'.format(transaction_id),
            'Unable to retrieve transaction id [{0}]'.format(transaction_id)
        )

    def transactions(self, search_criteria, start_date_utc, end_date_utc, count, offset):
        query = DotDict()
        if search_criteria:
            query.searchParameters = [x.to_dict() for x in search_criteria]
        query.startDate = datetime_to_cloudhub_format(start_date_utc)
        query.endDate = datetime_to_cloudhub_format((end_date_utc if end_date_utc else datetime.datetime.utcnow()))

        params = {
            'count': count,
            'offset': offset,
            'total': True
        }
        return self._post(path='transactions', data=json.dumps(query), params=params)


class CloudHubApplication(ApplicationBase):

    LOGGING_VERSION_1 = 'VERSION_1'
    LOGGING_VERSION_2 = 'VERSION_2'
    DESC = 'DESC'
    ASC = 'ASC'

    VALID_LOGGING_VERSIONS = {LOGGING_VERSION_1, LOGGING_VERSION_2}
    VALID_ORDER_BY_DATE = {DESC, ASC}

    @property
    def tracking(self):
        return CloudHubApplicationTracker(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self.app_info
        )

    @property
    def deployments(self):
        return self.find_deployments()

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

    def deploy(self, archive_to_deploy):

        payload = {
            "muleVersion": self.app_info["muleVersion"],
            "workers": str(self.app_info["workers"]),
            "workerType": self.app_info["workerType"]
        }

        properties = self.app_info["properties"]

        for prop in properties:
            payload["properties." + prop] = properties[prop]

        response = self._put(self.application_name, data=payload, files={'file': archive_to_deploy})
        if response.status_code != 200:
            raise ApplicationDeploymentError(
                "Failed to deploy application [{0}]".format(self.application_name),
                response.status_code
            )
