"""
Implementation of the "starting point" or "root" of the CloudHub API hierarchy.
"""
from cloudhub import CloudHubApplication, CloudHubApplicationTracker
from cloudhub.common import CloudHubApi


class CloudHub(CloudHubApi):
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

    def get_application_tracking(self, name):
        return CloudHubApplicationTracker(self.user_name, self.password, name, self.api_base_url)
