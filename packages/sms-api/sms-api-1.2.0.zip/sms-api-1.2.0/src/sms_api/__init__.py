
"""
    A simple python lib for send SMS easily using service https://easysms.4simple.org
"""


import requests

class SMS_Easy:
    """
    Main API class
    """
    API_URL = "https://api.4simple.org/%s"

    def __init__(self, user_id, auth_token, retries=5):
        """
        Provide account credentials here at class constructor.
        :param user_id: Your account User ID (located in https://easysms.4simple.org/user/panel/)
        :param auth_token: Your account Authentication Token (located in https://easysms.4simple.org/user/panel/)
        :return:
        """
        self.user_id = user_id
        self.auth_token = auth_token
        self.retries =retries

    def send_sms(self, to, body):
        """
        Send SMS using this function.

        :param to: recipient phone number. Remember add international country code prefix.
        :param body: sms text message to send.
        :return: A dictionary with the server response.
        When all was fine returned dictionary should be similar to:
            {'success': 'ok', 'pid': 123}
        The 'pid' var can be used to track sms in the system.
        When operation fails returned dictionary should be similar to:
            {'error': 'error description'}
        """
        payload = self.__build_payload({'to': to, 'body': body})
        return self.__send_payload("sms", payload)

    def get_account_balance(self):
        """
        Get your current account balance.

        :return: Accout balance or a dictionary with the error code response like: {'error': 'Login error'}
        """
        result = self.__send_payload("balance", self.__build_payload())
        if result.get("balance") is None:
            return result
        else:
            return result.get("balance")

    def get_sms_status(self, pid):
        """
        Get the delivered SMS status,

        :param pid: pid var returned while you send SMS
        :return: A dictionary with the server response.
        Examples of servers responses

        {'status': 'queued'}
            The status key is returned with the value set as the sms current status. Possible status values are:
                queued, when the sms is in the processing queue waiting to be delivered.
                success-delivered, when the sms was delivered successful.
                failed, when the sms delivery fails.

        {'error': 'error description'}
            The error key is returned if you submit incorrect credentials or use an invalid processing id pid.
            Some of the possible error details returned are:
                Login error, when incorrect credentials are provided.
                Pid error, when incorrect processing id pid is provided.
        """
        return self.__send_payload("status", self.__build_payload({'pid': pid}))

    def __send_payload(self, command, data):
        """
        Private function for internal usage, don't use it directly.
        :param url:
        :param data:
        :return:
        """
        for i in range(0, self.retries):
            try:
                with requests.Session() as s:
                    r = s.post(SMS_Easy.API_URL % command, data=data, headers={'Connection': 'close'})
                    s.close()
                    return r.json()
            except Exception, e:
                if i == self.retries - 1:
                    raise Exception("SMS API servers overloaded, request for: %s, fails after %s attempts." %
                                    (command, self.retries))

    def __build_payload(self, payload_dic={}):
        """
        Private function for internal usage, don't use it directly.
        :param payload_dic: extra payload dictionary
        :return: payload dictionary
        """
        payload = {'user_id': self.user_id, 'auth_token': self.auth_token}
        payload.update(payload_dic)
        return payload
