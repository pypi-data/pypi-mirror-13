# -*- coding: utf-8 -*-

"""AWS Opsworks Smooth Deploy
`Python Styling Guide <https://www.python.org/dev/peps/pep-0008/>`
`Docstring Guide <https://docs.python.org/devguide/documenting.html>`

This module provides functionalities to attach f

.. module:: opsworkssmoothdeploy
   :platform: Unix
.. moduleauthor:: Petra Barus <petra@urbanindo.com>
.. moduleauthor:: Rifki <rifki@urbanindo.com>
"""

import boto3
import json
import pycurl
import time
from StringIO import StringIO


opsworks_client = boto3.client('opsworks', region_name='us-east-1')
"""Boto client for Opsworks"""

elbclient = boto3.client('elb', region_name='ap-southeast-1')
"""Boto client for ELB"""

__MINIMUM_ATTACHED_INSTANCES__ = 1
__SLEEP_TIME__ = 10

def get_current_instance_id():
    """Get instance ID from HTTP request and returns it.
    """

    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://169.254.169.254/latest/meta-data/instance-id/')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()

    return body

def get_instance_stack(stack_id):
    """Get the instance stack of the instance id and returns it.
    :param stack_id The ID of the stack.
    """

    # Get Describe of this Stack
    response = opsworks_client.describe_instances(
        StackId=stack_id
    )
    ec2InstanceId = get_current_instance_id()
    for item in response['Instances']:
        if item['Status'] == 'online':
            if item['Ec2InstanceId'] == ec2InstanceId:
                return item['InstanceId']
    return ''

def get_elastic_load_balancer_id_from_stack(stack_id):
    """Get elastic load balancer that attached to a stack.
    :param stack_id The ID of the stack.
    """
    return

def get_layer_id_from_instance(instance_id):
    """Get layer id with which an instance being attached.
    :param instance_id The ID of the stack.
    """
    # Get Describe of this Instance
    response = opsworks_client.describe_instances(
        InstanceIds=[
            instance_id,
        ]
    )

    layerid =  response['Instances'][0]['LayerIds'][0]
    return layerid

def get_elastic_load_balancer_id_from_instance(instance_id):
    """Get elastic load balancer with which an instance being attached.
    :param instance_id The ID of the stack.
    """

    layerid =  get_layer_id_from_instance(instance_id)

    # Get describe of loadbalancer attached to specified layer
    response = opsworks_client.describe_elastic_load_balancers(
        LayerIds=[
            layerid,
        ]
    )

    if len(response['ElasticLoadBalancers']) > 0:
        return response['ElasticLoadBalancers'][0]['ElasticLoadBalancerName']
    else:
        raise ValueError('This instance is not attached to any Elastic Load Balancer')

def get_elastic_load_balancer_instance_count(elb):
    """Get elastic load balancer instance count from elb name
    :param elb The name of the elastic load balancer.
    """
    response = elbclient.describe_load_balancers(
        LoadBalancerNames=[
            elb,
        ]
    )
    layerInstanceCount = len(response['LoadBalancerDescriptions'][0]['Instances'])

    return layerInstanceCount

def get_layer_instance_count(layer_id):
    """Get instance count attached to a layer.
    :param layer_id the id of the layer.
    """
    # Get List of Describe Instance on specified layer
    response = opsworks_client.describe_instances(
        LayerId=layer_id
    )
    onlineInstance = 0
    for item in response['Instances']:
        if item['Status'] == 'online':
            onlineInstance += 1
    return 0

def attach_instance_to_elastic_load_balancer(instance_id, elb):
    """Attach an instance to load balancer.
    :param instance_id The ID of the instance to attach.
    :param elb         The name of the elastic load balancer.
    """

    response = elbclient.register_instances_with_load_balancer(
        LoadBalancerName=elb,
        Instances=[
            {
                'InstanceId': instance_id
            },
        ]
    )
    return response

def detach_instance_from_elastic_load_balancer(instance_id, elb):
    """Detach an instance to load balancer.
    :param instance_id The ID of the instance to detach.
    :param elb         The name of the elastic load balancer.
    """

    response = elbclient.deregister_instances_from_load_balancer(
        LoadBalancerName=elb,
        Instances=[
            {
                'InstanceId': instance_id
            },
        ]
    )
    pass

def detach(stack_id, minimum_instance = __MINIMUM_ATTACHED_INSTANCES__):
    """Detach current instance from the load balancer if the active instance
    is still in threshold.
    :param opsworks_stack_id The ID of the opsworks stack.
    """

    instanceId = get_current_instance_id()
    instanceStackId = get_instance_stack(stack_id)
    elbName = get_elastic_load_balancer_id_from_instance(instanceStackId)
    onlineInstance = get_elastic_load_balancer_instance_count(elbName)
    layerId = get_layer_id_from_instance(instanceStackId)
    layerInstanceCount = get_layer_instance_count(layerId)

    if layerInstanceCount != 1 and onlineInstance > 1:
        while(get_elastic_load_balancer_instance_count(elbName) < 2):
            print 'ELB has only 1 instance attached, wait for %s seconds...' % (__SLEEP_TIME__)
            time.sleep(__SLEEP_TIME__)

        detach_instance_from_elastic_load_balancer(instanceId, elbName)

        print 'success deregister instance %s' % (instanceId)
    else:
        print 'This Layer only contain 1 instance, detaching process bypassed.'
    pass

def attach(stack_id):
    """Attach current instance to load balancer.
    :param opsworks_stack_id The ID of the opsworks stack.
    """
    instanceId = get_current_instance_id()
    instanceStackId = get_instance_stack(stack_id)
    elbName = get_elastic_load_balancer_id_from_instance(instanceStackId)
    response = attach_instance_to_elastic_load_balancer(instanceId, elbName)
    print 'success register instance %s, ELB updated to %s instances running' % (instanceId, len(response['Instances']))
    pass
