#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import re
import json
import httplib
import datetime
import threading
import socket
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from nfv_common import debug
from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import fm
from nfv_vim import database

DLOG = debug.debug_get_logger('nfv_vim.webserver.webserver')

_lock = threading.Lock()
_token = None
_directory = None
_webserver_src_dir = '/'
_vim_api_ip = ''


def _bare_address_string(self):
    """
    Workaround to bypass the hostname resolution mechanism, so that
    the server can respond faster.
    """
    host, port = self.client_address[:2]
    return "%s" % host


BaseHTTPRequestHandler.address_string = _bare_address_string


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler
    """
    def do_GET(self):
        global _lock, _token

        if self.path == '/':
            with open(_webserver_src_dir + '/html/index.html', 'r') as f:
                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())

        elif self.path == '/windriver-favicon.ico':
            with open(_webserver_src_dir + '/images' + self.path, 'r') as f:
                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'image/x-icon')
                self.end_headers()
                self.wfile.write(f.read())

        elif re.search('/vim/overview', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                locked_hosts = 0
                unlocked_hosts = 0
                locking_hosts = 0
                unlocking_hosts = 0
                enabled_hosts = 0
                disabled_hosts = 0
                offline_hosts = 0
                failed_hosts = 0
                nfvi_enabled_hosts = 0

                hosts = database.database_host_get_list()
                for host in hosts:
                    if host.is_enabled():
                        enabled_hosts += 1

                    elif host.is_disabled():
                        disabled_hosts += 1

                    if host.nfvi_host_is_enabled():
                        nfvi_enabled_hosts += 1

                    if host.is_locked():
                        locked_hosts += 1
                    else:
                        unlocked_hosts += 1

                    if host.is_locking():
                        locking_hosts += 1

                    elif host.is_unlocking():
                        unlocking_hosts += 1

                    if host.is_offline():
                        offline_hosts += 1

                    if host.is_failed():
                        failed_hosts += 1

                total_hosts = len(hosts)

                locked_instances = 0
                unlocked_instances = 0
                enabled_instances = 0
                disabled_instances = 0
                failed_instances = 0
                powering_off_instances = 0
                pausing_instances = 0
                paused_instances = 0
                suspended_instances = 0
                suspending_instances = 0
                resizing_instances = 0
                rebooting_instances = 0
                rebuilding_instances = 0
                migrating_instances = 0
                deleting_instances = 0
                deleted_instances = 0

                instances = database.database_instance_get_list()
                for instance in instances:
                    if instance.is_locked():
                        locked_instances += 1
                    else:
                        unlocked_instances += 1

                    if instance.is_enabled():
                        enabled_instances += 1

                    if instance.is_disabled():
                        disabled_instances += 1

                    if instance.is_failed():
                        failed_instances += 1

                    if instance.is_powering_off():
                        powering_off_instances += 1

                    if instance.is_pausing():
                        pausing_instances += 1

                    if instance.is_paused():
                        paused_instances += 1

                    if instance.is_suspending():
                        suspending_instances += 1

                    if instance.is_suspended():
                        suspended_instances += 1

                    if instance.is_resizing():
                        resizing_instances += 1

                    if instance.is_rebooting():
                        rebooting_instances += 1

                    if instance.is_rebuilding():
                        rebuilding_instances += 1

                    if instance.is_migrating():
                        migrating_instances += 1

                    if instance.is_deleting():
                        deleting_instances += 1

                    if instance.is_deleted():
                        deleted_instances += 1

                total_instances = len(instances)

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    query_obj.group(1) + "(" +
                    json.dumps(
                        {'locked_hosts': locked_hosts,
                         'unlocked_hosts': unlocked_hosts,
                         'locking_hosts': locking_hosts,
                         'unlocking_hosts': unlocking_hosts,
                         'enabled_hosts': enabled_hosts,
                         'disabled_hosts': disabled_hosts,
                         'offline_hosts': offline_hosts,
                         'failed_hosts': failed_hosts,
                         'nfvi_enabled_hosts': nfvi_enabled_hosts,
                         'total_hosts': total_hosts,
                         'locked_instances': locked_instances,
                         'unlocked_instances': unlocked_instances,
                         'enabled_instances': enabled_instances,
                         'disabled_instances': disabled_instances,
                         'failed_instances': failed_instances,
                         'powering_off_instances': powering_off_instances,
                         'pausing_instances': pausing_instances,
                         'paused_instances': paused_instances,
                         'suspended_instances': suspended_instances,
                         'suspending_instances': suspending_instances,
                         'resizing_instances': resizing_instances,
                         'rebooting_instances': rebooting_instances,
                         'rebuilding_instances': rebuilding_instances,
                         'migrating_instances': migrating_instances,
                         'deleting_instances': deleting_instances,
                         'deleted_instances': deleted_instances,
                         'total_instances': total_instances,
                         'datetime': str(datetime.datetime.now())[:-3]
                         }) + ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/alarms', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                critical_alarms = 0
                major_alarms = 0
                minor_alarms = 0
                warning_alarms = 0
                indeterminate_alarms = 0

                _lock.acquire()
                if _token is None or _token.is_expired():
                    _token = openstack.get_token(_directory)
                _lock.release()

                result = fm.get_alarms(_token)
                if result.result_data:
                    for alarm in result.result_data['alarms']:
                        if 'critical' == alarm['severity']:
                            critical_alarms += 1
                        elif 'major' == alarm['severity']:
                            major_alarms += 1
                        elif 'minor' == alarm['severity']:
                            minor_alarms += 1
                        elif 'warning' == alarm['severity']:
                            warning_alarms += 1
                        else:
                            indeterminate_alarms += 1

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    query_obj.group(1) + "(" +
                    json.dumps(
                        {'critical_alarms': critical_alarms,
                         'major_alarms': major_alarms,
                         'minor_alarms': minor_alarms,
                         'warning_alarms': warning_alarms,
                         'indeterminate_alarms': indeterminate_alarms,
                         'datetime': str(datetime.datetime.now())[:-3]
                         }) + ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/systems', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                system_list = list()
                systems = database.database_system_get_list()
                for system in systems:
                    system_list.append(system.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'systems': system_list}) + ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/hosts', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                host_list = list()
                hosts = database.database_host_get_list()
                for host in hosts:
                    host_list.append(host.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'hosts': host_list}) + ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/host_groups', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                host_group_list = list()
                host_groups = database.database_host_group_get_list()
                for host_group in host_groups:
                    host_group_list.append(host_group.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'host_groups': host_group_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/host_aggregates', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                host_aggregate_list = list()
                host_aggregates = database.database_host_aggregate_get_list()
                for host_aggregate in host_aggregates:
                    host_aggregate_list.append(host_aggregate.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'host_aggregates':
                                             host_aggregate_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/hypervisors', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                hypervisor_list = list()
                hypervisors = database.database_hypervisor_get_list()
                for hypervisor in hypervisors:
                    hypervisor_list.append(hypervisor.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'hypervisors': hypervisor_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/instances', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                instance_list = list()
                instances = database.database_instance_get_list()
                for instance in instances:
                    instance_list.append(instance.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'instances': instance_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/instance_types', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                instance_type_list = list()
                instance_types = database.database_instance_type_get_list()
                for instance_type in instance_types:
                    instance_type_list.append(instance_type.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'instance_types':
                                             instance_type_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/instance_groups', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                instance_group_list = list()
                instance_groups = database.database_instance_group_get_list()
                for instance_group in instance_groups:
                    instance_group_list.append(instance_group.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'instance_groups':
                                             instance_group_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/images', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                image_list = list()
                images = database.database_image_get_list()
                for image in images:
                    image_list.append(image.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'images': image_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/volumes', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                volume_list = list()
                volumes = database.database_volume_get_list()
                for volume in volumes:
                    volume_list.append(volume.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'volumes': volume_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/volume_snapshots', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                volume_snapshot_list = list()
                volume_snapshots = database.database_volume_snapshot_get_list()
                for volume_snapshot in volume_snapshots:
                    volume_snapshot_list.append(volume_snapshot.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'volume_snapshots':
                                            volume_snapshot_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/subnets', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                subnet_list = list()
                subnets = database.database_subnet_get_list()
                for subnet in subnets:
                    subnet_list.append(subnet.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'subnets': subnet_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/vim/networks', self.path) is not None:
            query_obj = re.match(".*?callback=(.*)&.*", self.path)
            if query_obj is not None:
                network_list = list()
                networks = database.database_network_get_list()
                for network in networks:
                    network_list.append(network.as_dict())

                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(query_obj.group(1) + "(" +
                                 json.dumps({'networks': network_list}) +
                                 ")")
            else:
                self.send_response(httplib.BAD_REQUEST,
                                   'Bad Request: does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        elif re.search('/fonts', self.path) is not None:
            with open(_webserver_src_dir + self.path, 'r') as f:
                self.send_response(httplib.OK)
                self.send_header('Content-Type', 'application/font-woff')
                self.end_headers()
                self.wfile.write(f.read())

        else:
            mime_type = 'unsupported'
            send_reply = False
            if self.path.endswith(".html"):
                mime_type = 'text/html'
                send_reply = True
            elif self.path.endswith(".svg"):
                mime_type = 'image/svg+xml'
                send_reply = True
            elif self.path.endswith(".jpg"):
                mime_type = 'image/jpg'
                send_reply = True
            elif self.path.endswith(".gif"):
                mime_type = 'image/gif'
                send_reply = True
            elif self.path.endswith(".png"):
                mime_type = 'image/png'
                send_reply = True
            elif self.path.endswith(".ico"):
                mime_type = 'image/x-icon'
                send_reply = True
            elif self.path.endswith(".js"):
                mime_type = 'application/javascript'
                send_reply = True
            elif self.path.endswith(".css"):
                mime_type = 'text/css'
                send_reply = True
            elif self.path.endswith(".handlebars"):
                mime_type = 'text/x-handlebars-template'
                send_reply = True

            if send_reply:
                with open(_webserver_src_dir + self.path, 'r') as f:
                    self.send_response(httplib.OK)
                    self.send_header('Content-Type', mime_type)
                    self.end_headers()
                    self.wfile.write(f.read())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Threaded HTTP Server
    """
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer(object):
    """
    Simple HTTP Server
    """
    def __init__(self, webserver_config, nfvi_config, vim_api_config):
        global _webserver_src_dir, _directory, _vim_api_ip

        _webserver_src_dir = webserver_config['source_dir']

        ip = webserver_config['host']
        port = int(webserver_config['port'])
        if ':' in ip:
            # Configure server class to use IPv6
            ThreadedHTTPServer.address_family = socket.AF_INET6
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)
        self.server_thread = None

        config.load(nfvi_config['config_file'])
        _directory = openstack.get_directory(config)
        _vim_api_ip = vim_api_config['host']
        if ':' in _vim_api_ip:
            # Wrap IPv6 address for use in URLs
            _vim_api_ip = '[' + _vim_api_ip + ']'

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def wait_for_thread(self):
        if self.server_thread is not None:
            self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.wait_for_thread()
