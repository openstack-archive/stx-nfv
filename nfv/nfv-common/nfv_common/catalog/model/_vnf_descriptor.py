#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common.catalog.model._defs import CONNECTION_TYPE
from nfv_common.catalog.model._defs import CONNECTIVITY_TYPE

#
# Virtual Network Function Descriptor - Class Layout
#
# VNFD -+------ ConnectionPointVNFD
#       |
#       +------ VirtualLink
#       |
#       +------ DeploymentFlavor ------ ConstituentVDU
#       |
#       +------ VDU ------ VNFC ------ ConnectionPointVNFC
#


class VNFD(object):
    """
    Virtual Network Function Descriptor
        id: unique name for this vnfd
        vendor: who created this vnfd
        descriptor_version: the version of the vnf descriptor
        version: the version of the vnf software
        vdu: one or more VDU() objects
        virtual_link: zero or more VirtualLink() objects
        connection_point: one or more connection points described by
                          ConnectionPointVNFD() objects
        dependency: describes dependencies between vdus
        monitoring_parameter: monitoring parameters which can be tracked for
                              this vnf
        deployment_flavor: one or more DeploymentFlavor objects
        auto_scale_policy: describes the policy in terms of criteria and action
        manifest_file: a file that lists all files in the vnf package
        manifest_file_security: a file that contains a digest of each file that
                                it lists as part of the vnf package
    """
    def __init__(self, id):
        self.id = id
        self.vendor = None
        self.descriptor_version = None
        self.version = None
        self.vdu = []
        self.virtual_link = []
        self.connection_point = []
        self.dependency = []
        self.monitoring_parameter = []
        self.deployment_flavor = []
        self.auto_scale_policy = []
        self.manifest_file = []
        self.manifest_file_security = []


class ConnectionPointVNFD(object):
    """
    Connection Point of a Virtual Network Function Descriptor
        id: connection point identifier
        virtual_link_reference: references zero or more virtual links by their
                                identifiers
        type: type of connection
    """
    def __init__(self, id):
        self.id = id
        self.virtual_link_reference = None
        self.type = CONNECTION_TYPE.UNKNOWN


class VirtualLink(object):
    """
    Virtual Link
        id: unique identifier of this internal virtual link
        connectivity_type: the type of connectivity
        connection_points_references: 2 or more connection point identifiers
        root_requirement: describes the throughput of the link
        leaf_requirement: describes the throughput of the leaf connections
        qos: describes the qos options to be supported on the virtual link
        test_access: describes the test access facilities to be supported on
                     the virtual link
    """
    def __init__(self, id):
        self.id = id
        self.connectivity_type = CONNECTIVITY_TYPE.UNKNOWN
        self.connection_points_references = []
        self.root_requirement = None
        self.leaf_requirement = None
        self.qos = []
        self.test_access = None


class DeploymentFlavor(object):
    """
    Deployment Flavor
        id: vnf flavor identifier
        flavor_key: monitoring parameter and it's value against which this
                    flavor is being described
        constraint: zero or more deployment flavor constraints
        constituent_vdu: one or more ConstituentVDU() objects
    """
    def __init__(self, id):
        self.id = id
        self.flavor_key = None
        self.constraint = []
        self.constituent_vdu = []


class ConstituentVDU(object):
    """
    Constituent Virtual Deployment Unit
        vdu_reference: identifier of a vdu
        number_of_instances: number of vdu instances required
        constituent_vnfc: one or more vnfc identifiers that should be used for
                          this deployment
    """
    def __init__(self, vdu_reference):
        self.vdu_reference = vdu_reference
        self.number_of_instances = 0
        self.constituent_vnfc = []


class VDU(object):
    """
    Virtual Deployment Unit
        id: unique identifier for this vdu within the scope of the vnfd
        vm_image: a reference to the vm image, does not need to be specified in
                  the case of null containers
        computation_requirement: description of the required computation
                                 resource characteristics
        virtual_memory_resource_element: the virtual memory needed for this vdu
        virtual_network_bandwidth_resource: the network bandwidth needed for
                                            this vdu
        lifecycle_event: describes vnfc functional scripts/workflows for
                         specific lifecycle events
        constraint: vdu specific constraints
        high_availability: specifies the redundancy model
        scale_in_out: describes the minimum and maximum number of instances
                      that can be created when scaling
        vnfc: describes one or more VNFC() objects created using this vdu
        monitoring_parameter: zero or more monitoring parameters which can be
                              tracked for a vnfc based on this vdu
    """
    def __init__(self, id):
        self.id = id
        self.vm_image = None
        self.computation_requirement = None
        self.virtual_memory_resource_element = None
        self.virtual_network_bandwidth_resource = None
        self.lifecycle_event = []
        self.constraint = None
        self.high_availability = None
        self.scale_in_out = None
        self.vnfc = []
        self.monitoring_parameter = []


class VNFC(object):
    """
    Virtual Network Function Component
        id: unique vnfc identification within the namespace of a specific vnf
        connection_point: one or more network connections
    """
    def __init__(self, id):
        self.id = id
        self.connection_point = []


class ConnectionPointVNFC(object):
    """
    Connection Point of a Virtual Network Function Component
        id: connection point identifier
        virtual_link_reference: references zero or more internal virtual links
        type: type of network connection
    """
    def __init__(self, id):
        self.id = id
        self.virtual_link_reference = None
        self.type = CONNECTION_TYPE.UNKNOWN
