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

from __future__ import print_function

from functools import partial

import time
import requests
import threading
import Queue
import sys

from shimmercat.tools.api import RestApi, RequestFailedException
from shimmercat.tools.config_webdrivers import firefox_from_proxy_settings


def make_url(trained_domain, path):
    return "https://" + trained_domain + path


def training_worker(
        webdriver_factory,
        wait_time_seconds,
        work_queue
    ):
    webdriver = webdriver_factory()
    # Wait for a bit
    time.sleep(10.0)
    # Get stuff
    assert isinstance(work_queue, Queue.Queue)
    while not work_queue.empty():
        url = work_queue.get(block=False)
        if url is not None:
            webdriver.get(url)
#             time.sleep(0.5)
#             webdriver.execute_script("""
# window.scrollTo(0, document.documentElement.scrollTop || document.body.scrollTop)
#             """)
            time.sleep(wait_time_seconds)
    webdriver.quit()


def train_shimmercat(
    api,
    trained_domain,
    webdriver_factory,
    iterate_count = 4,
    wait_time_seconds = 15,
    dry_run = False
    ):
    #api = RestApi(cache_token, api_host, trained_domain, api_port )
    assert isinstance(api, RestApi)

    # Get a list of apexes
    r = api.get("nominal-apices")
    apexes = r.json()

    if dry_run:
        print("Apexes: ")
        for apex in apexes:
            print("  ", apex)
        return

    #apexes=["/__404.html"]

    api.set_no_triggers()
    api.set_learning()

    threads = []
    queues = []
    for i in range(iterate_count):
        queue = Queue.Queue()
        queues.append(queue)
        t = partial(training_worker, webdriver_factory, wait_time_seconds, queue)
        th = threading.Thread(
            target=t
            )
        th.start()
        threads.append(th)

    for apex in apexes:
        url = make_url(trained_domain, apex)
        for queue in queues:
            queue.put(url)

    for th in threads:
        th.join()
    api.learn()
    api.set_no_learning()


def fill_arg_parser(aparser):
    aparser.add_argument(
        "-5", "--socks5-port", help="SOCKS5 proxy port that ShimmerCat is running",
        dest='socks5_port',
        type=int,
        metavar='SOCKS5_PORT',
        default=2006
    )
    aparser.add_argument(
        "-q", "--socks5-host", help="SOCKS5 proxy host where ShimmerCat is running (should be local!!)",
        dest='socks5_host',
        type=str,
        metavar='SOCKS5_HOST',
        default='127.0.0.1'
    )
    aparser.add_argument(
        "-k", "--cache-token", help="Cache token (same as cache key for now)",
        type=str,
        dest='cache_token',
        metavar="CACHE_TOKEN",
        default=None
    )
    aparser.add_argument(
        "-s", "--ssl-port", help="Normal SSL port that ShimmerCat is using (for API calls)",
        type=int,
        dest="ssl_port",
        metavar="SSL_PORT",
        default=4043
    )
    aparser.add_argument(
        "site", help="Formal domain name to learn over (e.g., www.mysite.com), no port or scheme should be given",
        type=str
    )
    aparser.add_argument(
        "-d", "--dry-run",
        action="store_const",
        dest="dry_run",
        const=True, default=False,
        help="Only identify fetch roots",

    )
    aparser.add_argument(
        "--sleep-seconds", "-e", help="Time to give to a page to slowly load (we make it slow when learning)",
        type=float,
        default=15.0,
        metavar="SLEEP_SECONDS"
    )


def with_args(args):
    # At this time, let's just configure Firefox for the job
    webdriver_factory = partial(
        firefox_from_proxy_settings,
        args.socks5_host,
        args.socks5_port
    )
    api = RestApi(
        args.cache_token,
        args.socks5_host,
        args.site,
        args.ssl_port
    )

    if args.cache_token is None:
        print(
            "**Error: Please specify a cache token with the -k option. "
            "You can find the one of your server in the printed log of ShimmerCat, "
            "look for the phrase 'cache key' there.", file=sys.stderr)
        exit(2)

    try:
        train_shimmercat(
            api,
            args.site,
            webdriver_factory,
            dry_run=args.dry_run
        )
    except RequestFailedException as e:
        print("**Error: ", e.message, file=sys.stderr)
        exit(2)
    except requests.exceptions.ConnectionError as e:
        print("**Error: Could not connect to ShimmerCat. Please ensure the server is running with --devlove"
              " and the provided connection parameters are OK. ", file=sys.stderr
              )
        exit(2)

