# Copyright (c) 2015, Zunzun AB
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to
#    endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Use this module to train shimmercat automatically
#

import requests
from requests.packages import urllib3
urllib3.disable_warnings()


class RequestFailedException(Exception):
    def  __init__(self, message, errors=None):
        super(RequestFailedException, self).__init__(message)
        self.errors = errors

class RestApi(object):
    def __init__(self,
                 cache_token,
                 running_host,
                 nominal_host,
                 local_port
                 ):
        self._cache_token = cache_token
        self._running_host = running_host
        self._nominal_host = nominal_host
        self._local_port = local_port

    def make_url(self, trailing_url_part):
        return "https://" + self._running_host + ":" + str(self._local_port) + "/sc-api-v0/" + trailing_url_part + "/"

    def post(self, trailing_url_part, check_ok=True):
        url = self.make_url(trailing_url_part)
        r = requests.post(
            url,
            headers = self.access_headers(),
            verify=False
        )
        if check_ok and r.content != "OK":
            raise RequestFailedException("NoOK")
        if r.status_code != 200:
            raise RequestFailedException("No200")
        if not check_ok:
            return r.content

    def access_headers(self):
        return {
            "cache-token": self._cache_token,
            "host": self._nominal_host
        }

    def get(self, trailing_url_part):
        url = self.make_url(trailing_url_part)
        r = requests.get(
            url,
            headers = self.access_headers(),
            verify=False
        )
        if r.status_code != 200:
            raise RequestFailedException("REST request failed. Method: " + trailing_url_part)
        return r

    def set_no_learning(self):
        self.post("mode/set-no-learning")

    def set_learning(self):
        self.post("mode/set-learning")

    def set_no_triggers(self):
        self.post("mode/set-no-triggers")

    def set_triggers(self):
        self.post("mode/set-triggers")

    def get_apexes(self):
        r = self.get("nominal-apices")
        return r.json()

    def learn(self):
        r = self.post("learn", check_ok=False)
        print(r)