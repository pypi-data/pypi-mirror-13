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

import argparse
import sys

import sc_learn
import sc_chrome
import sc_instca


def main():
    parser = argparse.ArgumentParser(
        description="A tool to work with ShimmerCat. "
    )
    subparsers = parser.add_subparsers(dest="subparser_name",
                                       description="Use -h with each subcommand below for more details")
    sc_learn_parser = subparsers.add_parser('learn', help="Train server to perform HTTP/2 PUSH")
    sc_learn.fill_arg_parser(sc_learn_parser)

    sc_chrome_parser = subparsers.add_parser('chrome', help="Invoke Google Chrome with SOCKS5 proxy")
    sc_chrome.fill_arg_parser(sc_chrome_parser)

    if sys.platform == 'darwin':
        sc_instca_parser = subparsers.add_parser('addca', help="Install Mousebox's testing CA in the login keychain (Mac OS X)")
        sc_instca.fill_arg_parser( sc_instca_parser )

    args=parser.parse_args()

    if args.subparser_name == "learn":
        sc_learn.with_args(args)
    elif args.subparser_name == "chrome":
        sc_chrome.with_args(args)
    elif sys.platform == 'darwin':
        if args.subparser_name == 'addca':
            sc_instca.with_args(args)
        else:
            parser.print_usage()
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()