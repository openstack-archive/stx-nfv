#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import argparse
import codecs
import datetime
import os
import shutil
import signal
import sys
import tarfile
import time
import traceback
import uuid
import yaml

from jinja2 import Environment
from jinja2 import FileSystemLoader

from nfv_common import debug
from nfv_common import forensic
from nfv_plugins.nfvi_plugins import config

import tests

DLOG = debug.debug_get_logger('nfv_tests')


def process_signal_handler(signum, frame):
    """
    Test - Process Signal Handler
    """
    if signal.SIGINT == signum:
        raise KeyboardInterrupt
    else:
        print("Ignoring signal" % signum)


def process_initialize():
    """
    Test - Process Initialize
    """
    utf8_writer = codecs.getwriter('utf8')
    sys.stdout = utf8_writer(sys.stdout)
    debug.debug_initialize(config.CONF['debug'], 'NFV-TEST')
    forensic.forensic_initialize()


def process_finalize():
    """
    Test - Process Finalize
    """
    forensic.forensic_finalize()
    debug.debug_finalize()


def process_progress_marker_start(marker_name):

    space_str = '.' * (60 - len(marker_name))
    sys.stdout.write("%s  %s %s "
                     % (str(datetime.datetime.now())[:-3], marker_name,
                        space_str))
    sys.stdout.flush()


def process_progress_marker_end(marker_result):
    sys.stdout.write("%s\n" % marker_result)
    sys.stdout.flush()


def process_do_setup(loads_dir, setup_data):
    """
    Test - Process Do Setup
    """
    from nfv_plugins.nfvi_plugins.openstack import openstack
    from nfv_plugins.nfvi_plugins.openstack import nova
    from nfv_plugins.nfvi_plugins.openstack import cinder
    from nfv_plugins.nfvi_plugins.openstack import glance
    from nfv_plugins.nfvi_plugins.openstack import neutron

    directory = openstack.get_directory(config,
                                        openstack.SERVICE_CATEGORY.OPENSTACK)
    token = openstack.get_token(directory)

    result = nova.get_flavors(token)
    flavors = result.result_data.get('flavors', list())

    result = glance.get_images(token)
    images = result.result_data.get('images', list())

    result = cinder.get_volumes(token)
    volumes = result.result_data.get('volumes', list())

    result = neutron.get_networks(token)
    networks = result.result_data.get('networks', list())

    result = neutron.get_subnets(token)
    subnets = result.result_data.get('subnets', list())

    result = nova.get_servers(token)
    servers = result.result_data.get('servers', list())

    for resource in setup_data['resources']:
        if 'flavor' == resource['type']:
            process_progress_marker_start("Create flavor %s " % resource['name'])
            flavor = next((x for x in flavors
                           if x['name'] == resource['name']), None)
            if flavor is None:
                nova.create_flavor(token, resource['id'], resource['name'],
                                   resource['vcpus'], resource['ram_mb'],
                                   resource['disk_gb'],
                                   ephemeral_gb=resource['ephemeral_gb'],
                                   swap_mb=resource['swap_mb'])

                if 'extra_specs' in resource:
                    for extra_spec in resource['extra_specs']:
                        nova.set_flavor_extra_specs(
                            token, resource['id'],
                            {extra_spec['key']: str(extra_spec['value'])})

            process_progress_marker_end("[OKAY]")

    result = nova.get_flavors(token)
    flavors = result.result_data.get('flavors', list())

    for resource in setup_data['resources']:
        if 'image' == resource['type']:
            process_progress_marker_start("Create image %s " % resource['name'])
            image = next((x for x in images if x['name'] == resource['name']), None)
            if image is None:
                image_file = resource['file']
                if not os.path.isfile(image_file):
                    image_file = loads_dir + '/' + resource['file']
                    if not os.path.isfile(image_file):
                        process_progress_marker_end("[FAILED]")
                        print("Image file %s does not exist." % resource['file'])
                        return False

                image_data = glance.create_image(token, resource['name'],
                                                 resource['description'],
                                                 resource['container_format'],
                                                 resource['disk_format'],
                                                 resource['min_disk_size_gb'],
                                                 resource['min_memory_size_mb'],
                                                 resource['visibility'],
                                                 resource['protected'],
                                                 resource['properties']).result_data

                glance.upload_image_data_by_file(token, image_data['id'],
                                                 image_file)
            process_progress_marker_end("[OKAY]")

    result = glance.get_images(token)
    images = result.result_data.get('images', list())

    for resource in setup_data['resources']:
        if 'volume' == resource['type']:
            process_progress_marker_start("Create volume %s " % resource['name'])
            volume = next((x for x in volumes
                           if x['name'] == resource['name']), None)
            if volume is None:
                if resource['image_name'] is not None:
                    image = next((x for x in images
                                  if x['name'] == resource['image_name']), None)
                    if image is None:
                        process_progress_marker_end("[FAILED]")
                        print("Image %s for volume %s does not exist."
                              % (resource['image_name'], resource['name']))
                        return False

                    image_id = image['id']
                else:
                    image_id = None

                bootable = None
                if resource['bootable'] in ['YES', 'Yes', 'yes']:
                    bootable = True

                cinder.create_volume(token, resource['name'],
                                     resource['description'],
                                     resource['size_gb'],
                                     image_id,
                                     bootable=bootable)

                for _ in range(10):
                    time.sleep(5)
                    volumes = cinder.get_volumes(token).result_data
                    if volumes is not None:
                        volumes = volumes.get('volumes', list())
                        volume = next((x for x in volumes
                                       if x['name'] == resource['name']), None)
                        volume = cinder.get_volume(token, volume['id']).result_data
                        if 'available' == volume['volume']['status']:
                            break
                else:
                    process_progress_marker_end("[FAILED]")
                    print("Volume %s not create properly." % resource['name'])
                    return False
            process_progress_marker_end("[OKAY]")

    result = cinder.get_volumes(token)
    volumes = result.result_data.get('volumes', list())

    for resource in setup_data['resources']:
        if 'network' == resource['type']:
            process_progress_marker_start("Create network %s " % resource['name'])
            network = next((x for x in networks
                           if x['name'] == resource['name']), None)
            if network is None:
                neutron.create_network(token, resource['name'],
                                       resource['network_type'],
                                       resource['segmentation_id'],
                                       resource['physical_network'],
                                       resource['shared'])
            process_progress_marker_end("[OKAY]")

    result = neutron.get_networks(token)
    networks = result.result_data.get('networks', list())

    for resource in setup_data['resources']:
        if 'subnet' == resource['type']:
            process_progress_marker_start("Create subnet %s " % resource['name'])
            subnet = next((x for x in subnets
                           if x['name'] == resource['name']), None)
            if subnet is None:
                network = next((x for x in networks
                                if x['name'] == resource['network_name']), None)
                if network is None:
                    process_progress_marker_end("[FAILED]")
                    print("Network %s for subnet %s does not exist."
                          % (resource['network_name'], resource['name']))
                    return False

                neutron.create_subnet(token, network['id'], resource['name'],
                                      resource['ip_version'], resource['cidr'],
                                      resource['gateway_ip'],
                                      resource['dhcp_enabled'])
            process_progress_marker_end("[OKAY]")

    result = neutron.get_subnets(token)
    subnets = result.result_data.get('subnets', list())

    instance_created = False
    for resource in setup_data['resources']:
        if 'instance' == resource['type']:
            process_progress_marker_start("Create instance %s " % resource['name'])
            server = next((x for x in servers
                           if x['name'] == resource['name']), None)
            if server is None:
                flavor = next((x for x in flavors
                              if x['name'] == resource['flavor']), None)
                if flavor is None:
                    process_progress_marker_end("[FAILED]")
                    print("Can't find flavor %s for instance %s"
                          % (resource['flavor'], resource['name']))
                    return False

                if resource['image'] is not None:
                    image = next((x for x in images
                                  if x['name'] == resource['image']), None)
                    if image is None:
                        process_progress_marker_end("[FAILED]")
                        print("Can't find image %s for instance %s"
                              % (resource['image'], resource['name']))
                        return False

                    image_id = image['id']
                else:
                    image_id = None

                block_devices = list()
                for block_device in resource['block_devices']:
                    if 'volume' == block_device['type']:
                        volume = next((x for x in volumes
                                       if x['name'] == block_device['volume_name']),
                                      None)
                        if volume is None:
                            process_progress_marker_end("[FAILED]")
                            print("Can't find volume %s for instance %s"
                                  % (block_device['volume_name'], resource['name']))
                            return False

                        block_devices.append(
                            {'uuid': volume['id'],
                             'device_name': block_device['device_name'],
                             'source_type': block_device['source_type'],
                             'destination_type': block_device['destination_type'],
                             'boot_index': block_device['boot_index']})

                if 0 == len(block_devices):
                    block_devices = None

                network_ids = list()
                for network_name in resource['networks']:
                    network = next((x for x in networks
                                    if x['name'] == network_name), None)
                    if network is None:
                        process_progress_marker_end("[FAILED]")
                        print("Can't find network %s for instance %s"
                              % (network_name, resource['name']))
                        return False

                    network_ids.append({'uuid': network['id']})

                if 0 == len(network_ids):
                    network_ids = None

                nova.create_server(token, resource['name'], flavor['id'],
                                   image_id, block_devices, network_ids)

                for _ in range(10):
                    time.sleep(5)
                    result = nova.get_servers(token)
                    servers = result.result_data.get('servers', list())
                    if servers:
                        server = next((x for x in servers
                                       if x['name'] == resource['name']), None)
                        server = nova.get_server(token, server['id']).result_data
                        if 'ACTIVE' == server['server']['status']:
                            server_id = server['server']['id']
                            break
                else:
                    process_progress_marker_end("[FAILED]")
                    print("Server %s not created properly." % resource['name'])
                    return False

                for attached_volume in resource['attached_volumes']:
                    volume = next((x for x in volumes
                                   if x['name'] == attached_volume['volume_name']),
                                  None)
                    if volume is None:
                        process_progress_marker_end("[FAILED]")
                        print("Can't find volume %s for instance %s"
                              % (attached_volume['volume_name'], resource['name']))
                        return False

                    nova.attach_volume(token, server_id, volume['id'],
                                       attached_volume['device_name'])

                instance_created = True

            process_progress_marker_end("[OKAY]")

    if instance_created:
        # Allow time for instances to boot and guest client to start up
        # inside the each instance (in case it is being used). Timeout is long
        # because we are usually testing in Virtual Box.
        time.sleep(90)

    return True


def process_do_tests(test_data):
    """
    Test - Process Do Tests
    """
    test_output_dir = config.CONF['test-output']['dir']
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    os.makedirs(test_output_dir)

    test_set = list()

    for test in test_data['tests']:
        if 'pause_instance' == test['type']:
            test = tests.TestInstancePause(test['entity'], test['timeout'],
                                           test['guest_hb'])

        elif 'unpause_instance' == test['type']:
            test = tests.TestInstanceUnpause(test['entity'], test['timeout'],
                                             test['guest_hb'])

        elif 'suspend_instance' == test['type']:
            test = tests.TestInstanceSuspend(test['entity'], test['timeout'],
                                             test['guest_hb'])

        elif 'resume_instance' == test['type']:
            test = tests.TestInstanceResume(test['entity'], test['timeout'],
                                            test['guest_hb'])

        elif 'reboot_instance' == test['type']:
            test = tests.TestInstanceReboot(test['entity'], test['timeout'],
                                            test['hard_reset'], test['guest_hb'])

        elif 'rebuild_instance' == test['type']:
            test = tests.TestInstanceRebuild(test['entity'], test['timeout'],
                                             test['guest_hb'])

        elif 'stop_instance' == test['type']:
            test = tests.TestInstanceStop(test['entity'], test['timeout'],
                                          test['guest_hb'])

        elif 'start_instance' == test['type']:
            test = tests.TestInstanceStart(test['entity'], test['timeout'],
                                           test['guest_hb'])

        elif 'live_migrate_instance' == test['type']:
            test = tests.TestInstanceLiveMigrate(test['entity'], test['timeout'],
                                                 None, test['guest_hb'])

        elif 'cold_migrate_instance' == test['type']:
            test = tests.TestInstanceColdMigrate(test['entity'], test['timeout'],
                                                 None, test['guest_hb'])

        elif 'cold_migrate_confirm_instance' == test['type']:
            test = tests.TestInstanceColdMigrateConfirm(test['entity'],
                                                        test['timeout'],
                                                        test['guest_hb'])

        elif 'cold_migrate_revert_instance' == test['type']:
            test = tests.TestInstanceColdMigrateRevert(test['entity'],
                                                       test['timeout'],
                                                       test['guest_hb'])

        elif 'resize_instance' == test['type']:
            test = tests.TestInstanceResize(test['entity'], test['flavors'],
                                            test['timeout'], test['guest_hb'])

        elif 'resize_confirm_instance' == test['type']:
            test = tests.TestInstanceResizeConfirm(test['entity'], test['flavors'],
                                                   test['timeout'],
                                                   test['guest_hb'])

        elif 'resize_revert_instance' == test['type']:
            test = tests.TestInstanceResizeRevert(test['entity'], test['flavors'],
                                                  test['timeout'], test['guest_hb'])

        elif 'lock_host' == test['type']:
            test = tests.TestHostLock(test['entity'], test['instances'],
                                      test['timeout'])

        elif 'unlock_host' == test['type']:
            test = tests.TestHostUnlock(test['entity'], test['timeout'])

        else:
            test = None

        if test is not None:
            test_set.append(test)

    result_file = config.CONF['test-output']['result_file']

    start_datetime = datetime.datetime.now()

    for test in test_set:
        process_progress_marker_start("Test %s " % test.name)

        if not test.setup():
            process_progress_marker_end("[SETUP-FAILED]  (%s %s=%s)"
                                        % (str(test.end_datetime)[:-3], u"\u0394",
                                           str(test.elapsed_datetime)[:-3]))
            break

        if not test.run():
            process_progress_marker_end("[FAILED]  (%s %s=%s)"
                                        % (str(test.end_datetime)[:-3], u"\u0394",
                                           str(test.elapsed_datetime)[:-3]))
            break

        process_progress_marker_end("[OKAY]  (%s %s=%s)"
                                    % (str(test.end_datetime)[:-3], u"\u0394",
                                       str(test.elapsed_datetime)[:-3]))

        with open(result_file, 'a') as f:
            f.write("%s\n" % test.name.upper())

        test.save_customer_alarms(result_file)
        test.save_customer_alarm_history(result_file)
        test.save_customer_logs(result_file)
        time.sleep(1)

    tar_file = config.CONF['test-output']['tar_file']
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(test_output_dir, arcname=os.path.basename(test_output_dir))

    elapsed_datetime = datetime.datetime.now() - start_datetime
    sys.stdout.write("Total-Tests: %s     Execution-Time: %s\n"
                     % (len(test_set), str(elapsed_datetime)[:-3]))

    sys.stdout.flush()


def process_do_teardown(setup_data):
    """
    Test - Process Do Teardown
    """
    from nfv_plugins.nfvi_plugins.openstack import openstack
    from nfv_plugins.nfvi_plugins.openstack import nova
    from nfv_plugins.nfvi_plugins.openstack import cinder
    from nfv_plugins.nfvi_plugins.openstack import glance
    from nfv_plugins.nfvi_plugins.openstack import neutron

    directory = openstack.get_directory(config,
                                        openstack.SERVICE_CATEGORY.OPENSTACK)
    token = openstack.get_token(directory)

    result = nova.get_flavors(token)
    flavors = result.result_data.get('flavors', list())

    result = glance.get_images(token)
    images = result.result_data.get('images', list())

    result = cinder.get_volumes(token)
    volumes = result.result_data.get('volumes', list())

    result = neutron.get_networks(token)
    networks = result.result_data.get('networks', list())

    result = neutron.get_subnets(token)
    subnets = result.result_data.get('subnets', list())

    result = nova.get_servers(token)
    servers = result.result_data.get('servers', list())

    for resource in setup_data['resources']:
        if 'instance' == resource['type']:
            process_progress_marker_start("Delete instance %s " % resource['name'])
            server = next((x for x in servers
                           if x['name'] == resource['name']), None)
            if server is not None:
                nova.delete_server(token, server['id'])

                for _ in range(10):
                    time.sleep(5)
                    servers = nova.get_servers(token).result_data
                    if servers is not None:
                        servers = servers.get('servers', list())
                        server = next((x for x in servers
                                       if x['name'] == resource['name']), None)
                        if server is None:
                            break
                else:
                    process_progress_marker_end("[FAILED]")
                    print("Server %s not deleted." % resource['name'])
                    return False
            process_progress_marker_end("[OKAY]")

    for resource in setup_data['resources']:
        if 'subnet' == resource['type']:
            process_progress_marker_start("Delete subnet %s " % resource['name'])
            subnet = next((x for x in subnets
                           if x['name'] == resource['name']), None)
            if subnet is not None:
                neutron.delete_subnet(token, subnet['id'])
            process_progress_marker_end("[OKAY]")

    for resource in setup_data['resources']:
        if 'network' == resource['type']:
            process_progress_marker_start("Delete network %s " % resource['name'])
            network = next((x for x in networks
                           if x['name'] == resource['name']), None)
            if network is not None:
                neutron.delete_network(token, network['id'])
            process_progress_marker_end("[OKAY]")

    for resource in setup_data['resources']:
        if 'volume' == resource['type']:
            process_progress_marker_start("Delete volume %s " % resource['name'])
            volume = next((x for x in volumes
                           if x['name'] == resource['name']), None)
            if volume is not None:
                cinder.delete_volume(token, volume['id'])
            process_progress_marker_end("[OKAY]")

    for resource in setup_data['resources']:
        if 'image' == resource['type']:
            process_progress_marker_start("Delete image %s " % resource['name'])
            image = next((x for x in images if x['name'] == resource['name']), None)
            if image is not None:
                glance.delete_image(token, image['id'])
            process_progress_marker_end("[OKAY]")

    for resource in setup_data['resources']:
        if 'flavor' == resource['type']:
            process_progress_marker_start("Delete flavor %s " % resource['name'])
            flavor = next((x for x in flavors
                           if x['name'] == resource['name']), None)
            if flavor is not None:
                nova.delete_flavor(token, flavor['id'])
            process_progress_marker_end("[OKAY]")

    return True


def process_main():
    """
    Test - Process Main
    """
    try:
        want_teardown = False
        root_dir = os.path.dirname(__file__)
        data_dir = root_dir + '/data'
        loads_dir = data_dir + '/loads'
        setup_dir = data_dir + '/setup'
        tests_dir = data_dir + '/tests'
        j2_env = Environment(loader=FileSystemLoader([setup_dir, tests_dir]),
                             trim_blocks=True)
        j2_env.globals['uuid4'] = uuid.uuid4

        signal.signal(signal.SIGINT, process_signal_handler)

        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-c', '--config', help='configuration file')
        arg_parser.add_argument('-d', '--data', help='data file')
        arg_parser.add_argument('-s', '--setup', help='setup file')
        arg_parser.add_argument('-t', '--tests', help='tests file')
        arg_parser.add_argument('-r', '--repeat', help='repeat tests x times')
        arg_parser.add_argument('-f', '--forever', help='loop forever doing tests',
                                action='store_true')
        arg_parser.add_argument('-w', '--wipe', help='cleanup setup',
                                action='store_true')

        args = arg_parser.parse_args()

        if args.config:
            config.load(args.config)
        else:
            print("No configuration given.")
            sys.exit(1)

        if args.data:
            data_fill = yaml.load(open(data_dir + '/data/' + args.data + '.yaml'))
        else:
            print("No data file given.")
            sys.exit(1)

        if args.setup:
            setup_template = j2_env.get_template(args.setup + '.template')
            setup_yaml = setup_template.render(data_fill)
            setup_data = yaml.load(setup_yaml)
        else:
            print("No setup file given.")
            sys.exit(1)

        if args.tests:
            tests_template = j2_env.get_template(args.tests + '.template')
            tests_yaml = tests_template.render(data_fill)
            test_data = yaml.load(tests_yaml)
        else:
            print("No tests given.")
            sys.exit(1)

        if args.repeat:
            repeat = int(args.repeat)
            max_iteration_str = "max-iterations=%s" % repeat
        else:
            repeat = 0
            max_iteration_str = "single-execution"

        if args.forever:
            forever = True
            max_iteration_str = "forever"
        else:
            forever = False

        if args.wipe:
            want_teardown = True

        process_initialize()

        if want_teardown:
            setup_str = "===== Cleanup Previous Configuration"
            header_str = "%s %s" % (setup_str, '=' * (140 - len(setup_str)))
            footer_str = "%s" % '=' * 141

            sys.stdout.write("%s\n" % header_str)
            if not process_do_teardown(setup_data):
                print("Cleanup failed.")
                sys.exit(1)

            sys.stdout.write("%s\n" % footer_str)

            want_teardown = True
            time.sleep(60)

        setup_str = "===== Setup"
        header_str = "%s %s" % (setup_str, '=' * (140 - len(setup_str)))
        footer_str = "%s" % '=' * 141

        sys.stdout.write("%s\n" % header_str)
        if not process_do_setup(loads_dir, setup_data):
            print("Setup failed.")
            sys.exit(1)

        sys.stdout.write("%s\n" % footer_str)

        loop_i = 0
        while True:
            iteration_str = "===== Test Iteration %s (%s)" % (loop_i,
                                                              max_iteration_str)
            header_str = "%s %s" % (iteration_str, '=' * (140 - len(iteration_str)))
            footer_str = "%s" % '=' * 141

            sys.stdout.write("%s\n" % header_str)
            process_do_tests(test_data)
            sys.stdout.write("%s\n" % footer_str)
            loop_i += 1

            if not forever:
                if loop_i >= repeat:
                    break

        if want_teardown:
            setup_str = "===== Teardown"
            header_str = "%s %s" % (setup_str, '=' * (140 - len(setup_str)))
            footer_str = "%s" % '=' * 141

            sys.stdout.write("%s\n" % header_str)
            if not process_do_teardown(setup_data):
                print("Teardown failed.")
                sys.exit(1)

            sys.stdout.write("%s\n" % footer_str)

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")

    except Exception as e:
        print("Exception: %s" % e)
        traceback.print_exc()
        sys.exit(1)

    finally:
        process_finalize()


if __name__ == '__main__':
    process_main()
