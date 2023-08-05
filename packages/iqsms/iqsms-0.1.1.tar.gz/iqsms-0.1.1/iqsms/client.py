import six

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import json

__author__ = 'Zhuravlev Kirill <kazhuravlev@fastmail.com>'


class IQsmsException(Exception):
    pass


class JSONClient(object):
    """Class for using http://iqsms.ru/api/api_json/ service"""

    base_url = 'http://json.gate.iqsms.ru/'

    def __init__(self, api_login, api_password, timeout=None):
        assert isinstance(api_login, six.string_types)
        assert isinstance(api_password, six.string_types)
        assert timeout is None or isinstance(timeout, float)

        self._timeout = timeout
        self._login = api_login
        self._password = api_password

    def _send_request(self, uri, params=None):
        if params is None:
            params = {}

        params['login'] = self._login
        params['password'] = self._password
        data = json.dumps(params)

        request_url = self.base_url + uri + '/'
        try:
            if six.PY3:
                f = urlopen(
                    url=request_url,
                    data=bytes(data, encoding='utf-8'),
                    timeout=self._timeout
                )
                result = f.read()
                return json.loads(str(result, encoding='utf-8'))
            else:
                f = urlopen(request_url, data, timeout=self._timeout)
                result = f.read()
                return json.loads(result)

        except Exception as e:
            raise IQsmsException(e)

    def send(self, messages, queue_name=None, schedule_time=None):
        """
        Send SMS
        http://iqsms.ru/api/api_json/#send
        """

        assert isinstance(messages, list)
        assert queue_name is None or isinstance(queue_name, six.string_types)
        assert schedule_time is None or isinstance(schedule_time, six.string_types)

        params = {'messages': messages}

        if queue_name is not None:
            params['statusQueueName'] = queue_name

        if schedule_time is not None:
            params['scheduleTime'] = schedule_time

        return self._send_request('send', params)

    def status(self, messages):
        """
        Retrieve status of SMS
        http://iqsms.ru/api/api_json/#status
        """

        assert isinstance(messages, list)

        params = {'messages': messages}

        return self._send_request('status', params)

    def status_queue(self, queue_name, limit):
        """
        Retrieve latest statuses from queue
        http://iqsms.ru/api/api_json/#statusQueue
        """

        assert isinstance(queue_name, six.string_types)
        assert isinstance(limit, six.integer_types)

        params = {'statusQueueName': queue_name,
                  'statusQueueLimit': limit}

        return self._send_request('statusQueue', params)

    def credits(self):
        """
        Retrieve current credit balance
        http://iqsms.ru/api/api_json/#credits
        """

        return self._send_request('credits')

    def senders(self):
        """
        Retrieve available senders
        http://iqsms.ru/api/api_json/#senders
        """

        return self._send_request('senders')
