# -*- coding: utf-8 -*-

"""AWS Opsworks Smooth Deploy
`Python Styling Guide <https://www.python.org/dev/peps/pep-0008/>`
`Docstring Guide <https://docs.python.org/devguide/documenting.html>`

This module provides role generation for instances to have ability to attach
and detach itself from its load balancer.

.. module:: opsworkssmoothdeploy
   :platform: Unix
.. moduleauthor:: Petra Barus <petra@urbanindo.com>
.. moduleauthor:: Rifki <rifki@urbanindo.com>
"""

import boto3
import json

opsworks_client = None
"""Boto client for Opsworks"""

elb_client = None
"""Boto client for ELB"""

iam_client = None
"""Boto client for IAM to attach the policy"""

def generate_role(opsworks_stack_id):
    """Generate role ID from opsworks
    :param opsworks_stack_id The ID of the opsworks stack to process
    """
    opsworks_client = boto3.client('opsworks', region_name='us-east-1')
    elbclient = boto3.client('elb')
    #response = client.describe_layers(
    #    StackId = stack_id
    #)
    #ARN arn:aws:elasticloadbalancing:region:my-account-id:loadbalancer/load-balancer-name
    #response = opsworksclient.describe_elastic_load_balancers(
    #    LayerIds = [
    #        'layer'
    #    ]
    #)
    #print json.dumps(response)
