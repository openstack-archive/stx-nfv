#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import sys
import argparse
try:
    # python3
    from urllib.request import HTTPHandler, build_opener, install_opener
except ImportError:
    # python2
    from urllib2 import HTTPHandler, build_opener, install_opener


from nfv_client import sw_update


def process_main(argv=sys.argv[1:]):  # pylint: disable=dangerous-default-value
    """
    Client - Main
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--os-auth-url', default=None)
        parser.add_argument('--os-project-name', default=None)
        parser.add_argument('--os-project-domain-name', default=None)
        parser.add_argument('--os-username', default=None)
        parser.add_argument('--os-password', default=None)
        parser.add_argument('--os-user-domain-name', default=None)
        parser.add_argument('--os-region-name', default=None)
        parser.add_argument('--os-interface', default=None)

        commands = parser.add_subparsers(title='Commands', metavar='')

        # Software Patch Commands
        sw_patch_parser = commands.add_parser('patch-strategy',
                                              help='Patch Strategy')
        sw_patch_parser.set_defaults(cmd_area='patch-strategy')

        sw_patch_cmds = sw_patch_parser.add_subparsers(
            title='Software Patch Commands', metavar='')

        sw_patch_create_strategy_cmd \
            = sw_patch_cmds.add_parser('create', help='Create a strategy')
        sw_patch_create_strategy_cmd.set_defaults(cmd='create')
        sw_patch_create_strategy_cmd.add_argument(
            '--controller-apply-type', default=sw_update.APPLY_TYPE_SERIAL,
            choices=[sw_update.APPLY_TYPE_SERIAL, sw_update.APPLY_TYPE_IGNORE],
            help='defaults to serial')
        sw_patch_create_strategy_cmd.add_argument(
            '--storage-apply-type', default=sw_update.APPLY_TYPE_SERIAL,
            choices=[sw_update.APPLY_TYPE_SERIAL, sw_update.APPLY_TYPE_PARALLEL,
                     sw_update.APPLY_TYPE_IGNORE],
            help='defaults to serial')
        sw_patch_create_strategy_cmd.add_argument(
            '--compute-apply-type', default=sw_update.APPLY_TYPE_SERIAL,
            choices=[sw_update.APPLY_TYPE_SERIAL, sw_update.APPLY_TYPE_PARALLEL,
                     sw_update.APPLY_TYPE_IGNORE],
            help='defaults to serial')
        sw_patch_create_strategy_cmd.add_argument(
            '--max-parallel-compute-hosts', type=int, choices=range(2, 101),
            help='maximum compute hosts to patch in parallel')
        sw_patch_create_strategy_cmd.add_argument(
            '--instance-action', default=sw_update.INSTANCE_ACTION_STOP_START,
            choices=[sw_update.INSTANCE_ACTION_MIGRATE,
                     sw_update.INSTANCE_ACTION_STOP_START],
            help='defaults to stop-start')
        sw_patch_create_strategy_cmd.add_argument(
            '--alarm-restrictions', default=sw_update.ALARM_RESTRICTIONS_STRICT,
            choices=[sw_update.ALARM_RESTRICTIONS_STRICT,
                     sw_update.ALARM_RESTRICTIONS_RELAXED],
            help='defaults to strict')

        sw_patch_delete_strategy_cmd \
            = sw_patch_cmds.add_parser('delete', help='Delete a strategy')
        sw_patch_delete_strategy_cmd.set_defaults(cmd='delete')
        sw_patch_delete_strategy_cmd.add_argument(
            '--force', action='store_true', help=argparse.SUPPRESS)

        sw_patch_apply_strategy_cmd \
            = sw_patch_cmds.add_parser('apply', help='Apply a strategy')
        sw_patch_apply_strategy_cmd.set_defaults(cmd='apply')
        sw_patch_apply_strategy_cmd.add_argument(
            '--stage-id', default=None, help='stage identifier to apply')

        sw_patch_abort_strategy_cmd \
            = sw_patch_cmds.add_parser('abort', help='Abort a strategy')
        sw_patch_abort_strategy_cmd.set_defaults(cmd='abort')
        sw_patch_abort_strategy_cmd.add_argument(
            '--stage-id', help='stage identifier to abort')

        sw_patch_show_strategy_cmd \
            = sw_patch_cmds.add_parser('show', help='Show a strategy')
        sw_patch_show_strategy_cmd.set_defaults(cmd='show')
        sw_patch_show_strategy_cmd.add_argument(
            '--details', action='store_true', help='show strategy details')

        # Software Upgrade Commands
        sw_upgrade_parser = commands.add_parser('upgrade-strategy',
                                                help='Upgrade Strategy')
        sw_upgrade_parser.set_defaults(cmd_area='upgrade-strategy')

        sw_upgrade_cmds = sw_upgrade_parser.add_subparsers(
            title='Software Upgrade Commands', metavar='')

        sw_upgrade_create_strategy_cmd \
            = sw_upgrade_cmds.add_parser('create', help='Create a strategy')
        sw_upgrade_create_strategy_cmd.set_defaults(cmd='create')
        sw_upgrade_create_strategy_cmd.add_argument(
            '--storage-apply-type', default=sw_update.APPLY_TYPE_SERIAL,
            choices=[sw_update.APPLY_TYPE_SERIAL, sw_update.APPLY_TYPE_PARALLEL,
                     sw_update.APPLY_TYPE_IGNORE],
            help='defaults to serial')
        sw_upgrade_create_strategy_cmd.add_argument(
            '--compute-apply-type', default=sw_update.APPLY_TYPE_SERIAL,
            choices=[sw_update.APPLY_TYPE_SERIAL, sw_update.APPLY_TYPE_PARALLEL,
                     sw_update.APPLY_TYPE_IGNORE],
            help='defaults to serial')
        sw_upgrade_create_strategy_cmd.add_argument(
            '--max-parallel-compute-hosts', type=int, choices=range(2, 11),
            help='maximum compute hosts to upgrade in parallel')
        # Disable support for --start-upgrade as it was not completed
        # sw_upgrade_create_strategy_cmd.add_argument(
        #     '--start-upgrade', action='store_true',
        #     help=argparse.SUPPRESS)
        sw_upgrade_create_strategy_cmd.add_argument(
            '--complete-upgrade', action='store_true', help=argparse.SUPPRESS)
        sw_upgrade_create_strategy_cmd.add_argument(
            '--alarm-restrictions', default=sw_update.ALARM_RESTRICTIONS_STRICT,
            choices=[sw_update.ALARM_RESTRICTIONS_STRICT,
                     sw_update.ALARM_RESTRICTIONS_RELAXED],
            help='defaults to strict')

        sw_upgrade_delete_strategy_cmd \
            = sw_upgrade_cmds.add_parser('delete', help='Delete a strategy')
        sw_upgrade_delete_strategy_cmd.set_defaults(cmd='delete')
        sw_upgrade_delete_strategy_cmd.add_argument(
            '--force', action='store_true', help=argparse.SUPPRESS)

        sw_upgrade_apply_strategy_cmd \
            = sw_upgrade_cmds.add_parser('apply', help='Apply a strategy')
        sw_upgrade_apply_strategy_cmd.set_defaults(cmd='apply')
        sw_upgrade_apply_strategy_cmd.add_argument(
            '--stage-id', default=None, help='stage identifier to apply')

        sw_upgrade_abort_strategy_cmd \
            = sw_upgrade_cmds.add_parser('abort', help='Abort a strategy')
        sw_upgrade_abort_strategy_cmd.set_defaults(cmd='abort')
        sw_upgrade_abort_strategy_cmd.add_argument(
            '--stage-id', help='stage identifier to abort')

        sw_upgrade_show_strategy_cmd \
            = sw_upgrade_cmds.add_parser('show', help='Show a strategy')
        sw_upgrade_show_strategy_cmd.set_defaults(cmd='show')
        sw_upgrade_show_strategy_cmd.add_argument(
            '--details', action='store_true', help='show strategy details')

        args = parser.parse_args(argv)

        if args.debug:
            # Enable Debug
            handler = HTTPHandler(debuglevel=1)
            opener = build_opener(handler)
            install_opener(opener)

        if args.os_auth_url is None:
            args.os_auth_url = os.environ.get('OS_AUTH_URL', None)

        if args.os_project_name is None:
            args.os_project_name = os.environ.get('OS_PROJECT_NAME', None)

        if args.os_project_domain_name is None:
            args.os_project_domain_name \
                = os.environ.get('OS_PROJECT_DOMAIN_NAME', None)

        if args.os_username is None:
            args.os_username = os.environ.get('OS_USERNAME', None)

        if args.os_password is None:
            args.os_password = os.environ.get('OS_PASSWORD', None)

        if args.os_user_domain_name is None:
            args.os_user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME', None)

        if args.os_region_name is None:
            args.os_region_name = os.environ.get('OS_REGION_NAME', None)

        if args.os_interface is None:
            args.os_interface = os.environ.get('OS_INTERFACE', None)

        if args.os_auth_url is None:
            print("Authentication URI not given")
            return

        if args.os_project_name is None:
            print("Project name not given")
            return

        if args.os_project_domain_name is None:
            print("Project domain name not given")
            return

        if args.os_username is None:
            print("Username not given")
            return

        if args.os_password is None:
            print("User password not given")
            return

        if args.os_user_domain_name is None:
            print("User domain name not given")
            return

        if args.os_region_name is None:
            print("Openstack region name not given")
            return

        if args.os_interface is None:
            print("Openstack interface not given")
            return

        if 'patch-strategy' == args.cmd_area:
            if 'create' == args.cmd:
                sw_update.create_strategy(
                    args.os_auth_url, args.os_project_name,
                    args.os_project_domain_name, args.os_username, args.os_password,
                    args.os_user_domain_name, args.os_region_name,
                    args.os_interface,
                    sw_update.STRATEGY_NAME_SW_PATCH,
                    args.controller_apply_type,
                    args.storage_apply_type, sw_update.APPLY_TYPE_IGNORE,
                    args.compute_apply_type,
                    args.max_parallel_compute_hosts,
                    args.instance_action,
                    args.alarm_restrictions)

            elif 'delete' == args.cmd:
                sw_update.delete_strategy(args.os_auth_url, args.os_project_name,
                                          args.os_project_domain_name,
                                          args.os_username, args.os_password,
                                          args.os_user_domain_name,
                                          args.os_region_name, args.os_interface,
                                          sw_update.STRATEGY_NAME_SW_PATCH,
                                          args.force)

            elif 'apply' == args.cmd:
                sw_update.apply_strategy(args.os_auth_url, args.os_project_name,
                                         args.os_project_domain_name,
                                         args.os_username, args.os_password,
                                         args.os_user_domain_name,
                                         args.os_region_name, args.os_interface,
                                         sw_update.STRATEGY_NAME_SW_PATCH,
                                         args.stage_id)

            elif 'abort' == args.cmd:
                sw_update.abort_strategy(args.os_auth_url, args.os_project_name,
                                         args.os_project_domain_name,
                                         args.os_username, args.os_password,
                                         args.os_user_domain_name,
                                         args.os_region_name, args.os_interface,
                                         sw_update.STRATEGY_NAME_SW_PATCH,
                                         args.stage_id)

            elif 'show' == args.cmd:
                sw_update.show_strategy(args.os_auth_url, args.os_project_name,
                                        args.os_project_domain_name,
                                        args.os_username, args.os_password,
                                        args.os_user_domain_name,
                                        args.os_region_name, args.os_interface,
                                        sw_update.STRATEGY_NAME_SW_PATCH,
                                        args.details)

            else:
                raise ValueError("Unknown command, %s, given for patch-strategy"
                                 % args.cmd)
        elif 'upgrade-strategy' == args.cmd_area:
            if 'create' == args.cmd:
                sw_update.create_strategy(
                    args.os_auth_url, args.os_project_name,
                    args.os_project_domain_name, args.os_username, args.os_password,
                    args.os_user_domain_name, args.os_region_name,
                    args.os_interface,
                    sw_update.STRATEGY_NAME_SW_UPGRADE,
                    sw_update.APPLY_TYPE_IGNORE,
                    args.storage_apply_type, sw_update.APPLY_TYPE_IGNORE,
                    args.compute_apply_type,
                    args.max_parallel_compute_hosts,
                    None, args.alarm_restrictions,
                    # start_upgrade=args.start_upgrade,
                    complete_upgrade=args.complete_upgrade
                )

            elif 'delete' == args.cmd:
                sw_update.delete_strategy(args.os_auth_url, args.os_project_name,
                                          args.os_project_domain_name,
                                          args.os_username, args.os_password,
                                          args.os_user_domain_name,
                                          args.os_region_name, args.os_interface,
                                          sw_update.STRATEGY_NAME_SW_UPGRADE,
                                          args.force)

            elif 'apply' == args.cmd:
                sw_update.apply_strategy(args.os_auth_url, args.os_project_name,
                                         args.os_project_domain_name,
                                         args.os_username, args.os_password,
                                         args.os_user_domain_name,
                                         args.os_region_name, args.os_interface,
                                         sw_update.STRATEGY_NAME_SW_UPGRADE,
                                         args.stage_id)

            elif 'abort' == args.cmd:
                sw_update.abort_strategy(args.os_auth_url, args.os_project_name,
                                         args.os_project_domain_name,
                                         args.os_username, args.os_password,
                                         args.os_user_domain_name,
                                         args.os_region_name, args.os_interface,
                                         sw_update.STRATEGY_NAME_SW_UPGRADE,
                                         args.stage_id)

            elif 'show' == args.cmd:
                sw_update.show_strategy(args.os_auth_url, args.os_project_name,
                                        args.os_project_domain_name,
                                        args.os_username, args.os_password,
                                        args.os_user_domain_name,
                                        args.os_region_name, args.os_interface,
                                        sw_update.STRATEGY_NAME_SW_UPGRADE,
                                        args.details)

            else:
                raise ValueError("Unknown command, %s, given for upgrade-strategy"
                                 % args.cmd)
        else:
            raise ValueError("Unknown command area, %s, given" % args.cmd_area)

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")

    except Exception as e:  # pylint: disable=broad-except
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    process_main(sys.argv[1:])
