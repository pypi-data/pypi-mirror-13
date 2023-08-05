from plytix.retailers.services import ResponseList, ResponseDict
from plytix.retailers.exceptions import PlytixRetailersAPIError, BadResponseError
from plytix.retailers.fields import *
from plytix.retailers.services import BaseEndpoint


class DataEndpoint(BaseEndpoint):
    """ Endpoint to consume brand resources.
    """
    _BASE_ENDPOINT = 'data'
    _BASE_ENDPOINT_RESOURCE = None

    def track(self, customer_id, site_id, actions):
        """
        :param customer_id: Customer identifier.
        :param site_id: Origin site identifer.
        :param actions: Actions to track. List of dictionaries: [{'action_name': 'action', 'action_value': value},]
        :return: Response.
        """
        data = {
            INPUT_DATA_TRACK_CUSTOMER_ID: customer_id,
            INPUT_DATA_TRACK_SITE_ID: site_id,
            INPUT_DATA_TRACK_ACTIONS: actions,
        }

        # TODO Validate data

        endpoint = self._BASE_ENDPOINT + '/track'
        try:
            response = super(DataEndpoint, self)._raw_post(endpoint=endpoint, data=data)
            return response.ok
        except Exception as e:
            raise e

    def get_actions(self):
        """ Get all actions.
        :return: List of actions.
        """
        endpoint = self._BASE_ENDPOINT + '/actions'
        try:
            response = super(DataEndpoint, self)._raw_get(endpoint=endpoint)
            return response.json()[INPUT_DATA_GET_ACTIONS_ACTIONS]
        except Exception as e:
            raise e