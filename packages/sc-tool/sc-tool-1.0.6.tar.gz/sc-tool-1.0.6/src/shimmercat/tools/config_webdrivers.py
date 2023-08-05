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

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def firefox_from_proxy_settings(
    proxy_host='127.0.0.1',
    proxy_port=2006
    ):
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference('network.proxy.type', 1)
    firefox_profile.set_preference('network.proxy.socks', proxy_host)
    firefox_profile.set_preference('network.proxy.socks_port', proxy_port)
    firefox_profile.set_preference('network.proxy.socks_remote_dns', True)
    firefox_profile.set_preference('network.prefetch-next', False)
    driver = webdriver.Firefox(firefox_profile=firefox_profile)

    return driver