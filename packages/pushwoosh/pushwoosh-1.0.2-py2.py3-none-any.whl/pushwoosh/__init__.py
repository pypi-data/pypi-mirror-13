"""
Interact with the Pushwoosh API
"""

import json
import six
if six.PY2:
    import httplib
if six.PY3:
    import http.client

SERVER = 'cp.pushwoosh.com'
URL = 'https://cp.pushwoosh.com/json/1.3/'

class Pushwoosh(object):
    """
    Object for interacting with Pushwoosh
    """

    def __init__(self, apitoken, appcode, debug=True):
        """
        Create the object
        """
        self.apitoken = apitoken
        self.appcode = appcode
        self.debug = debug

    def __pwCall(self, method, data):
        """
        Communicate with the server
        """
        # Get data
        url = URL + method
        request = json.dumps(data)

        # Make the request
        if six.PY2:
            conn = httplib.HTTPSConnection(SERVER)
        if six.PY3:
            conn = http.client.HTTPSConnection(SERVER)
        headers = {'Content-type': 'application/json'}
        conn.request('POST', url, body=request, headers=headers)
        resp = conn.getresponse()
        return resp.status, resp.read()

    def create_message(self, pushes, sendDate='now', link=None, ios_badges = 0):
        """
        Create the message
        """
        # Populate a dictionary with the data
        push_list = []
        for item in pushes:
            push = {}
            push['send_date'] = sendDate
            push['content'] = item['text']
            push['link'] = link
            push['ios_badges'] = ios_badges

            # If a list of devices is specified, add that to the push data
            if 'devices' in item:
                push['devices'] = item['devices']

            # If conditions set, add that to the push data
            if 'conditions' in item:
                push['conditions'] = [item['conditions']]

            # If data set, add that to the push data
            if 'data' in item:
                push['data'] = item['data']

            # Append to the list
            push_list.append(push)

        # Create a dictionary to hold the whole request
        request = {}
        request['application'] = self.appcode
        request['auth'] = self.apitoken
        request['notifications'] = push_list
        data = {}
        data['request'] = request

        # Call the API
        status, content  = self.__pwCall('createMessage', data)
        return status, content
        pass
