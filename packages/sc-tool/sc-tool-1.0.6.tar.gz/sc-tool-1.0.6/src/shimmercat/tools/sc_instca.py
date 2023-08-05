
from __future__ import print_function

import sys
import subprocess as sp
import os
import glob
import os.path

# Use a command like this one...
# security add-trusted-cert -d -r trustRoot   -p ssl -k /Users/alcides/Library/Keychains/login.keychain ~/.config/mousebox/mousebox_ca_root_tuqrep.pem

def fill_arg_parser(aparser):
    aparser.add_argument(
        "--dry-run", "-r",
        action='store_const',
        const=True,
        dest='dry_run',
        help="Just print the command that would add the certificate(s)"
        )

def get_mousebox_path():
    return os.path.join(os.environ["HOME"], ".config/mousebox")

def make_cmd(username, cert_path):
    return [
        "security",
        "add-trusted-cert", "-r", "trustRoot",
        "-p", "ssl", "-k", "/Users/{0}/Library/Keychains/login.keychain".format(username),
        cert_path
    ]

def make_commands():
    mouse_box_path = get_mousebox_path()
    username = os.environ["USER"]
    return [
        make_cmd(username, cert_path) for cert_path in glob.glob(
            os.path.join(mouse_box_path, "mousebox_ca_root_*.pem")
        )
    ]

def with_args(args):
    cmds = make_commands()
    if args.dry_run:
        for cmd in cmds:
            print(" ".join(cmd))
    else:
        for cmd in cmds:
            try:
                print(" ".join(cmd))
                sp.check_call(cmd)
            except sp.CalledProcessError:
                print("**ERROR: Failed adding certificate, exiting", file=sys.stderr)
                exit(2)
