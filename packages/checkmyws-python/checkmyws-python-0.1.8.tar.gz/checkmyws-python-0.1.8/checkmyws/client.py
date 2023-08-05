# -*- coding: utf-8 -*-
"""
python client for www.checkmy.ws
"""
import sys
PY26 = sys.version_info[0] == 2 and sys.version_info[1] == 6

import logging
import requests
import hashlib
import time

from checkmyws.exception import CheckmywsError

requests.packages.urllib3.disable_warnings()

BASE_URL = "https://api.checkmy.ws/api"


class CheckmywsClient(object):

    def __init__(self, proxy=None, verify=True,
                 login=None, passwd=None, token=None, url=None):

        self.logger = logging.getLogger("CheckmywsClient")
        self.logger.debug("Initialize")

        self.session = requests.Session()
        self.proxies = None
        self.verify = verify
        self.url = url

        if self.url is None:
            self.url = BASE_URL

        if "api.dev" in self.url:
            self.verify = False

        self.logger.debug("Url: %s, Verify: %s", self.url, self.verify)

        self.login = login
        self.passwd = passwd
        self.token = token
        self.authed = False

        self.last_request = None

        if passwd and len(passwd) != 40:
            self.passwd = hashlib.sha1(passwd.encode('utf8')).hexdigest()

        if PY26:
            self.verify = False

        if proxy is not None:
            self.proxies = {
                "http": proxy,
                "https": proxy
            }

    def request(self, path, method="GET", params=None, data=None,
                status_code=200):
            """
            Make a http request to API
            """
            url = "{0}{1}".format(self.url, path)

            if params is None:
                params = {}

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                verify=self.verify,
                proxies=self.proxies
            )

            if response.status_code == status_code:
                self.last_request = time.time()
                return response
            else:
                raise CheckmywsError(response)

    def signin(self):
        if self.authed:
            age = time.time() - self.last_request
            if age < 3600:
                return

        data = {
            'login': self.login,
            'passwd': self.passwd
        }

        if self.token:
            data['token'] = self.token

        self.request(path="/auth/signin", method="POST", data=data)
        self.authed = True

    def logout(self):
        self.request(path="/auth/logout", method="GET")
        self.authed = False

    def status(self, check_id):
        path = "/status/{0}".format(check_id)
        response = self.request(path=path, method="GET")
        return response.json()

    def workers(self):
        self.signin()
        response = self.request(path="/workers", method="GET")
        return response.json()

    def checks(self):
        self.signin()
        response = self.request(path="/checks", method="GET")
        return response.json()

    def check_create(self, data):
        self.signin()
        response = self.request(path="/checks", method="POST", data=data)
        return response.json()

    def check(self, check_id, data=None):
        self.signin()
        path = "/checks/{0}".format(check_id)

        if data is None:
            response = self.request(path=path, method="GET")
        else:
            response = self.request(path=path, method="POST", data=data)

        return response.json()

    def check_overview(self, check_id):
        self.signin()
        path = "/overview/{0}".format(check_id)
        response = self.request(path=path, method="GET")
        return response.json()

    def check_delete(self, check_id):
        self.signin()
        path = "/checks/{0}".format(check_id)
        self.request(path=path, method="DELETE")
