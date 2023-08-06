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

__POLICY_NAME__ = 'AwsOpsworksSmoothDeployPolicy'

def generate_role(opsworks_stack_id):
    """Generate role ID from opsworks
    :param opsworks_stack_id The ID of the opsworks stack to process
    """
    opsworks_client = boto3.client('opsworks', region_name='us-east-1')
    iam_client = boto3.client('iam')

    response = opsworks_client.describe_stacks(
        StackIds=[
            opsworks_stack_id,
        ]
    )

    if len(response['Stacks']):
        instanceProfile = response['Stacks'][0]['DefaultInstanceProfileArn']
    else:
        raise ValueError('Stack Not Found')

    posStart = instanceProfile.find('instance-profile/') + 17
    instanceProfile = instanceProfile[posStart:]

    try:
        response = iam_client.get_instance_profile(
            InstanceProfileName=instanceProfile
        )
        roleName = response['InstanceProfile']['Roles'][0]['RoleName']
        pass
    except Exception, e:
        raise e

    policyDocument = """
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1455875911000",
                "Effect": "Allow",
                "Action": [
                    "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                    "elasticloadbalancing:DescribeLoadBalancers",
                    "elasticloadbalancing:RegisterInstancesWithLoadBalancer"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Sid": "Stmt1455876823000",
                "Effect": "Allow",
                "Action": [
                    "opsworks:DescribeElasticLoadBalancers",
                    "opsworks:DescribeInstances",
                    "opsworks:DescribeLayers",
                    "opsworks:DescribeStacks"
                ],
                "Resource": [
                    "arn:aws:opsworks:ap-southeast-1:395685607895:stack/*"
                ]
            }
        ]
    }
    """
    policyDocument = json.loads(policyDocument)
    try:
        response = iam_client.put_role_policy(
            RoleName=roleName,
            PolicyName=__POLICY_NAME__,
            PolicyDocument=json.dumps(policyDocument)
        )
        print 'Role ' + __POLICY_NAME__ + ' added to instance profile'
        pass
    except Exception, e:
        raise e
    pass
