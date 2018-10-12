#
# Copyright (c) 2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import httplib
import kubernetes
from kubernetes.client.rest import ApiException

from nfv_common import debug
from nfv_common.helpers import Result

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.clients.kubernetes_client')


def get_client():
    kubernetes.config.load_kube_config('/etc/kubernetes/admin.conf')

    # Workaround: Turn off SSL/TLS verification
    c = kubernetes.client.Configuration()
    c.verify_ssl = False
    kubernetes.client.Configuration.set_default(c)

    return kubernetes.client.CoreV1Api()


def taint_node(node_name, effect, key, value):
    """
    Apply a taint to a node
    """
    # Get the client.
    kube_client = get_client()

    # Retrieve the node to access any existing taints.
    try:
        response = kube_client.read_node(node_name)
    except ApiException as e:
        if e.status == httplib.NOT_FOUND:
            # In some cases we may attempt to taint a node that exists in
            # the VIM, but not yet in kubernetes (e.g. when the node is first
            # being configured). Ignore the failure.
            DLOG.info("Not tainting node %s because it doesn't exist" %
                      node_name)
            return
        else:
            raise

    add_taint = True
    taints = response.spec.taints
    if taints is not None:
        for taint in taints:
            # Taints must be unique by key and effect
            if taint.key == key and taint.effect == effect:
                add_taint = False
                if taint.value != value:
                    msg = ("Duplicate value - key: %s effect: %s "
                           "value: %s new value %s" % (key, effect,
                                                       taint.value, value))
                    DLOG.error(msg)
                    raise Exception(msg)
                else:
                    # This taint already exists
                    break

    if add_taint:
        DLOG.info("Adding %s=%s:%s taint to node %s" % (key, value, effect,
                                                        node_name))
        # Preserve any existing taints
        if taints is not None:
            body = {"spec": {"taints": taints}}
        else:
            body = {"spec": {"taints": []}}
        # Add our new taint
        new_taint = {"key": key, "value": value, "effect": effect}
        body["spec"]["taints"].append(new_taint)
        response = kube_client.patch_node(node_name, body)

    return Result(response)


def untaint_node(node_name, effect, key):
    """
    Remove a taint from a node
    """
    # Get the client.
    kube_client = get_client()

    # Retrieve the node to access any existing taints.
    response = kube_client.read_node(node_name)

    remove_taint = False
    taints = response.spec.taints
    if taints is not None:
        for taint in taints:
            # Taints must be unique by key and effect
            if taint.key == key and taint.effect == effect:
                remove_taint = True
                break

    if remove_taint:
        DLOG.info("Removing %s:%s taint from node %s" % (key, effect,
                                                         node_name))
        # Preserve any existing taints
        updated_taints = [taint for taint in taints if taint.key != key or
                          taint.effect != effect]
        body = {"spec": {"taints": updated_taints}}
        response = kube_client.patch_node(node_name, body)

    return Result(response)


def delete_node(node_name):
    """
    Delete a node
    """
    # Get the client.
    kube_client = get_client()

    # Delete the node
    body = kubernetes.client.V1DeleteOptions()
    response = kube_client.delete_node(node_name, body)

    return Result(response)
