#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
import argparse
import config
import time
import socket
import httplib

from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import ceilometer
from nfv_plugins.nfvi_plugins.openstack import cinder
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import glance
from nfv_plugins.nfvi_plugins.openstack import guest
from nfv_plugins.nfvi_plugins.openstack import keystone
from nfv_plugins.nfvi_plugins.openstack import neutron
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import heat
from nfv_plugins.nfvi_plugins.openstack import sysinv


def keystone_unit_tests(token, test_config):
    """
    Run through the unit tests for keystone
    """
    print "[KEYSTONE UNIT TESTS]"
    tenants = keystone.get_tenants(token)
    print "List of tenants: %s" % tenants


def ceilometer_unit_tests(token, test_config):
    """
    Run through the unit tests for ceilometer
    """
    print "[CEILOMETER UNIT TESTS]"
    meters = ceilometer.get_meters(token)
    print "List of meters: %s" % meters

    alarms = ceilometer.get_alarms(token)
    print "List of alarms: %s" % alarms


def sysinv_unit_tests(token, test_config):
    """
    Run through the unit tests for system inventory
    """
    print "[SYSINV UNIT TESTS]"
    system_info = sysinv.get_system_info(token)
    print "System information: %s" % system_info

    hosts = sysinv.get_hosts(token)
    print "List of hosts: %s" % hosts

#    for host in hosts['ihosts']:
        #host_uuid = host['uuid']
        #host_name = host['hostname']

        # Needs proper setup since system inventory will reject the disable
        # until a lock is really started.
        #response = sysinv.notify_host_services_disabled(token, host_uuid)
        #print ("Notify host-services-disabled: host_uuid=%s, "
        #       "host_name=%s, response=%s" % (host_uuid, host_name, response))

        #response = sysinv.notify_host_services_disable_failed(token, host_uuid)
        #print ("Notify host-services-disable failed: host_uuid=%s, "
        #       "host_name=%s, response=%s" % (host_uuid, host_name, response))

        #response = sysinv.notify_host_services_enabled(token, host_uuid)
        #print ("Notify host-services enabled: host_uuid=%s, host_name=%s, "
        #       "response=%s" % (host_uuid, host_name, response))


def glance_unit_tests(token, test_config):
    """
    Run through the unit tests for glance
    """
    print "[GLANCE UNIT TESTS]"

    images = glance.get_images(token)
    print "List of images: %s" % images

    for image in images['images']:
        print "Deleting image: %s" % image
        glance.delete_image(token, image['id'])

    image = glance.create_image(token, "image-test", "", "bare", "qcow2",
                                1, 512, "public", False, None)
    print "Created image: %s" % image

    glance.upload_image_data_by_url(token, image['id'],
                                    test_config['image_url'])

    image = glance.get_image(token, image['id'])
    print "Image details: %s" % image

    image = glance.create_image(token, "image-test2", "", "bare", "qcow2",
                                2, 1024, "private", False, None)
    print "Created image: %s" % image

    glance.upload_image_data_by_file(token, image['id'],
                                     test_config['image_file'])

    image = glance.get_image(token, image['id'])
    print "Image details: %s" % image

    try:
        glance.delete_image(token, 5555)
        print "Error Delete non-existent image"

    except exceptions.OpenStackRestAPIException as e:
        if 404 == e.http_status_code:
            print "Delete non-existent image, returned not found."
        else:
            print "Failed to delete non-existent image, error=%s" % e

    except exceptions.OpenStackException as e:
        print "Failed to delete non-existent image, error=%s." % e


def cinder_unit_tests(token, test_config):
    """
    Run through the unit tests for cinder
    """
    print "[CINDER UNIT TESTS]"

    servers = nova.get_servers(token)
    for server in servers['servers']:
        nova.delete_server(token, server['id'])

    while servers['servers']:
        servers = nova.get_servers(token)
        time.sleep(0.5)

    volumes = cinder.get_volumes(token)
    print "List of volumes: %s" % volumes

    for volume in volumes['volumes']:
        print "Deleting volume: %s" % volume
        cinder.delete_volume(token, volume['id'])

    volume = cinder.create_volume(token, "volume-test", "", 1)
    print "Created volume: %s" % volume

    volume = cinder.get_volume(token, volume['volume']['id'])
    print "Fetched volume: %s" % volume


def neutron_unit_tests(token, test_config):
    """
    Run through the unit tests for neutron
    """
    print "[NEUTRON UNIT TESTS]"

    response = neutron.create_host_services(token, test_config['host_name'],
                                            test_config['host_uuid'])
    print "Host-Services create response: %s" % response

    response = neutron.disable_host_services(token, test_config['host_uuid'])
    print "Host-Services disable response: %s" % response

    response = neutron.enable_host_services(token,  test_config['host_uuid'])
    print "Host-Services enable response: %s" % response

    response = neutron.disable_host_services(token, test_config['host_uuid'])
    print "Host-Services disable response: %s" % response

    response = neutron.delete_host_services(token, test_config['host_uuid'])
    print "Host-Services delete response: %s" % response

    response = neutron.create_host_services(token, test_config['host_name'],
                                            test_config['host_uuid'])
    print "Host-Services create response: %s" % response

    response = neutron.enable_host_services(token,  test_config['host_uuid'])
    print "Host-Services enable response: %s" % response

    servers = nova.get_servers(token)
    for server in servers['servers']:
        nova.delete_server(token, server['id'])

    while servers['servers']:
        servers = nova.get_servers(token)
        time.sleep(0.5)

    networks = neutron.get_networks(token)
    print "List of networks: %s" % networks

    for network in networks['networks']:
        print "Deleting network: %s" % network
        neutron.delete_network(token, network['id'])

    network = neutron.create_network(token, 'network-test', 'vlan', 450,
                                     'physnet0', False)
    print "Created network: %s" % network

    network = neutron.update_network(token, network['network']['id'],
                                     neutron.NETWORK_ADMIN_STATE.DOWN, True)
    print "Updated network: %s" % network

    subnets = neutron.get_subnets(token)
    print "List of subnets: %s" % subnets

    for subnet in subnets['subnets']:
        print "Deleting subnet: %s" % subnet
        neutron.delete_subnet(token, subnet['id'])

    subnet = neutron.create_subnet(token, network['network']['id'],
                                   'subnet-test', 4, '192.168.101.0/24',
                                   '192.168.101.1', True)
    print "Created subnet: %s" % subnet

    subnet = neutron.update_subnet(token, subnet['subnet']['id'],
                                   delete_gateway=True, dhcp_enabled=False)
    print "Updated subnet: %s" % subnet

    subnet = neutron.get_subnet(token, subnet['subnet']['id'])
    print "Fetched subnet: %s" % subnet


def nova_unit_tests(token, test_config):
    """
    Run through the unit tests for nova
    """
    print "[NOVA UNIT TESTS]"

    response = nova.create_host_services(token, test_config['host_name'])
    print "Host-Services create response: %s" % response

    response = nova.disable_host_services(token, test_config['host_name'])
    print "Host-Services disable response: %s" % response

    response = nova.enable_host_services(token, test_config['host_name'])
    print "Host-Services enable response: %s" % response

    response = nova.disable_host_services(token, test_config['host_name'])
    print "Host-Services disable response: %s" % response

    # NOTE: if you do a delete of the host-services, the hypervisors are
    # deleted and will not be populated again until nova-compute is
    # restarted even if you re-create and enable the host-services.
    #response = nova.delete_host_services(token, test_config['host_name'])
    #print "Host-Services delete response: %s" % response

    response = nova.create_host_services(token, test_config['host_name'])
    print "Host-Services create response: %s" % response

    response = nova.enable_host_services(token, test_config['host_name'])
    print "Host-Services enable response: %s" % response

    hypervisors = nova.get_hypervisors(token)
    print "List of hypervisors: %s" % hypervisors

    for hypervisor in hypervisors['hypervisors']:
        visor = nova.get_hypervisor(token, hypervisor['id'])
        print "Fetched hypervisor: %s" % visor

    flavors = nova.get_flavors(token)
    print "List of flavors: %s" % flavors

    for flavor in flavors['flavors']:
        print "Deleting flavor: %s" % flavor
        nova.delete_flavor(token, flavor['id'])

    flavor = nova.create_flavor(token, 1, "flavor-test", 1, 512, 1)
    print "Created flavor: %s" % flavor

    servers = nova.get_servers(token)
    print "List of servers: %s" % servers

    deleted_servers = servers.copy()
    for server in servers['servers']:
        print "Deleting server: %s" % server
        nova.delete_server(token, server['id'])

    while servers['servers']:
        servers = nova.get_servers(token)
        time.sleep(0.5)
    print "Servers deleted: %s" % deleted_servers['servers']

    images = glance.get_images(token)
    image = next(image for image in images['images']
                 if image['name'] == 'image-test')

    networks = neutron.get_networks(token)
    network = next(network for network in networks['networks']
                   if network['name'] == 'network-test')

    networks = list()
    networks.append({'uuid': network['id']})

    server = nova.create_server(token, "server-test-with-glance",
                                flavor['flavor']['id'], image['id'],
                                networks=networks)
    print "Created server: %s" % server

    server = nova.get_server(token, server['server']['id'])
    print "Fetched server: %s" % server

    volumes = cinder.get_volumes(token)
    volume = next(volume for volume in volumes['volumes']
                  if volume['name'] == 'volume-test')

    block_devices = list()
    block_devices.append({'uuid': volume['id'],
                          'device_name': '/dev/sda1',
                          'source_type': 'volume',
                          'destination_type': 'volume',
                          'boot_index': '0'})

    server = nova.create_server(token, "server-test-with-cinder",
                                flavor['flavor']['id'], image['id'],
                                block_devices=block_devices,
                                networks=networks)
    status = None
    while 'ACTIVE' != status:
        server = nova.get_server(token, server['server']['id'])
        status = server['server']['status']
        time.sleep(0.5)
    print "Created server: %s" % server

    server = nova.get_server(token, server['server']['id'])
    print "Fetched server: %s" % server

    nova.reboot_server(token, server['server']['id'], nova.VM_REBOOT_TYPE.HARD)
    status = None
    while 'ACTIVE' != status:
        server = nova.get_server(token, server['server']['id'])
        status = server['server']['status']
        time.sleep(0.5)
    print "Hard rebooted server: %s" % server['server']['name']

    status = None
    nova.rebuild_server(token, server['server']['id'], server['server']['name'],
                        image['id'])
    while 'ACTIVE' != status:
        server = nova.get_server(token, server['server']['id'])
        status = server['server']['status']
        time.sleep(0.5)
    print "Rebuilt server: %s" % server['server']['name']

    servers = nova.get_servers(token)
    print "List of servers: %s" % servers

    for server in servers['servers']:
        nova.delete_server(token, server['id'])

    while servers['servers']:
        servers = nova.get_servers(token)
        time.sleep(0.5)
    print "Servers deleted"


def heat_unit_tests(token, test_config):
    """
    Run through the unit tests for heat
    """
    print "[HEAT UNIT TESTS]"

    versions = heat.get_versions(token)
    print "Versions: %s" % versions

    stacks = heat.get_stacks(token)
    print "List of stacks: %s" % stacks

    for stack in stacks['stacks']:
        heat.delete_stack(token, stack['stack_name'],  stack['id'])

    stacks = heat.get_stacks(token)
    while stacks['stacks']:
        stacks = heat.get_stacks(token)
        time.sleep(0.5)
        print "%s" % stacks
    print "Stacks deleted"

    with open("/root/OS_Nova_Flavor.yaml", "r") as template_file:
        template = template_file.read()

    stack = heat.create_stack(token, "Test_Flavor", template)
    print "Stack created: %s" % stack

    stack = heat.get_stack(token, stack['id'])
    print "Fetched stack: %s" % stack

    heat.delete_stack(token, stack['stack']['stack_name'],
                      stack['stack']['id'])
    print "Stack deleted"


def guest_unit_tests(token, test_config):
    """
    Run through the unit tests for Host and Guest Service
    """
    print "[GUEST UNIT TESTS]"

    response = guest.host_services_create(token, test_config['host_uuid'],
                                          test_config['host_name'])
    print "host_services_create response: %s" % response

    response = guest.host_services_enable(token, test_config['host_uuid'],
                                          test_config['host_name'])
    print "host_services_enable response: %s" % response

    response = guest.host_services_disable(token, test_config['host_uuid'],
                                           test_config['host_name'])
    print "host_services_disable response: %s" % response

    response = guest.host_services_query(token, test_config['host_uuid'],
                                         test_config['host_name'])
    print "host_services_query response: %s" % response

    response = guest.host_services_delete(token, test_config['host_uuid'])
    print "host_services_delete response: %s" % response

    services = ['heartbeat', 'massage']
    response = guest.guest_services_create(token, test_config['instance_uuid'],
                                           test_config['host_name'],
                                           services)
    print "guest_services_create response: %s" % response

    services = {'heartbeat': 'enabled', 'massage': 'disabled'}
    response = guest.guest_services_set(token,
                                        test_config['instance_uuid'],
                                        test_config['host_name'],
                                        services)
    print "guest_services_set response: %s" % response

    response = guest.guest_services_query(token, test_config['instance_uuid'])
    print "guest_services_query response: %s" % response

    response = guest.guest_services_delete(token, test_config['instance_uuid'])
    print "guest_services_delete response: %s" % response


def rest_api_unit_tests(token, test_config):
    """
    Run through the unit tests for Host and Guest Service
    """
    print "[REST-API UNIT TESTS]"

    # This will hang the rest-api request as no message body is ever written.
    conn = httplib.HTTPConnection('localhost:30001')
    conn.connect()
    conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)
    conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
    conn.send('PATCH /nfvi-plugins/v1/hosts/compute-0 HTTP/1.1 \r\n')
    conn.send('Content-Type: application/json\r\n')
    conn.send('Content-Length: 0\r\n')
    #conn.send('Content-Length: 20\r\n')
    conn.send('\r\n')

    msg = conn.sock.recv(1)
    print msg
    time.sleep(20)
    #fp = conn.sock.makefile('rb')
    #line = fp.read(1)
    #line = fp.readline()
    #print line
    time.sleep(20)
    try:
        conn.send('\r\n')
    except BaseException as e:
        # Expected that the VIM will give up on this request and close
        # the connection.
        print e


def do_unit_tests(test_set=None, rest_api_debug=False, test_config=None):
    """
    NFVI Plugins Unit Tests
    """
    if rest_api_debug:
        # Enable debugging of request and response headers for rest-api calls
        import urllib2
        handler = urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    directory = openstack.get_directory(config)
    token = openstack.get_token(directory)

    if test_set is None:
        test_set = ['keystone', 'ceilometer', 'sysinv', 'glance', 'cinder',
                    'neutron', 'nova', 'heat', 'guest']

    print "-" * 80
    if 'keystone' in test_set:
        keystone_unit_tests(token, test_config)
        print "-" * 80

    if 'ceilometer' in test_set:
        ceilometer_unit_tests(token, test_config)
        print "-" * 80

    if 'sysinv' in test_set:
        sysinv_unit_tests(token, test_config)
        print "-" * 80

    if 'glance' in test_set:
        glance_unit_tests(token, test_config)
        print "-" * 80

    if 'cinder' in test_set:
        cinder_unit_tests(token, test_config)
        print "-" * 80

    if 'neutron' in test_set:
        neutron_unit_tests(token, test_config)
        print "-" * 80

    if 'nova' in test_set:
        nova_unit_tests(token, test_config)
        print "-" * 80

    if 'heat' in test_set:
        heat_unit_tests(token, test_config)
        print "-" * 80

    if 'guest' in test_set:
        guest_unit_tests(token, test_config)
        print "-" * 80

    if 'rest-api' in test_set:
        rest_api_unit_tests(token, test_config)
        print "-" * 80


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='configuration file')
    parser.add_argument('-t', '--test_set', help='test set')
    parser.add_argument('-d', '--rest_api_debug', help='rest api debug enable')

    args = parser.parse_args()

    # TODO: Port this into a unit test config file and
    # TODO: fix the config object to handle multiple config files
    test_config = dict()
    test_config['host_name'] = 'compute-101'
    test_config['host_uuid'] = '93ad7f54-f31c-44c8-b44f-2e0ccfb62aa7'
    test_config['image_url'] = 'http://192.168.204.15:4545/file/cirros-0.3.0-x86_64-disk.img'
    test_config['image_file'] = '/scratch/cirros-0.3.0-x86_64-disk.img'
    test_config['instance_uuid'] = '82a41f2c-994a-46e0-8d8b-bf1d6b3258ac'

    config.load(args.config)

    do_unit_tests(args.test_set, args.rest_api_debug, test_config)
