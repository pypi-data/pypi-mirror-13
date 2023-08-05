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


import sys
import subprocess as sp
import os
import os.path


def get_chrome_exe():
    if sys.platform == 'darwin':
        chrome_exe = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    else:
        chrome_exe = 'google-chrome'
    return chrome_exe

def get_default_alt_dir():
    return os.path.join( os.environ["HOME"], "sc-chrome-profile")

def fill_arg_parser(aparser):
    aparser.add_argument(
        "-5", "--socks5-port", help="SOCKS6 proxy port that ShimmerCat is running on",
        dest='socks5_port',
        type=int,
        metavar='SOCKS5_PORT',
        default=2006
    )
    aparser.add_argument(
        "-x", "--executable", help="Chrome executable to use",
        dest="executable",
        type=str,
        metavar="EXECUTABLE",
        default=get_chrome_exe()
    )
    aparser.add_argument(
        "-d", "--user-dir", help="New user dir for chrome",
        dest="user_dir",
        type=str,
        metavar="USER_DIR",
        default=get_default_alt_dir()
    )

def with_args(args):
    proxy_port = args.socks5_port
    executable=args.executable
    print("About to execute Google Chrome")
    user_dir = os.path.join(args.user_dir, "socks5_port_" + str(proxy_port))
    p = sp.Popen(
        [
            executable,
            "--user-data-dir={0}".format(user_dir),
            "--proxy-server=socks5://127.0.0.1:{0}".format(proxy_port),
            "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1"
        ]
    )
    print("Chrome should be opening now")

