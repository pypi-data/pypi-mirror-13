# -*- coding: utf-8 -*-

"""AWS Opsworks Smooth Deploy
`Python Styling Guide <https://www.python.org/dev/peps/pep-0008/>`
`Docstring Guide <https://docs.python.org/devguide/documenting.html>`

This module provides main script for the executable.
.. module:: opsworkssmoothdeploy
   :platform: Unix
.. moduleauthor:: Petra Barus <petra@urbanindo.com>
.. moduleauthor:: Rifki <rifki@urbanindo.com>
"""

import sys
import argparse
from .role import generate_role
from .deploy import attach, detach, get_instance_stack

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="detach, attach")
    parser.add_argument("--opsworks-stack-id", help="Stack ID")
    args = parser.parse_args()

    if args.action == 'role':
        generate_role(args.opsworks_stack_id)
    elif args.action == 'attach':
        attach(args.opsworks_stack_id)
        pass
    elif args.action == 'detach':
        detach(args.opsworks_stack_id)
        pass
    elif args.action == 'getinstance':
        print get_instance_stack(args.opsworks_stack_id)
