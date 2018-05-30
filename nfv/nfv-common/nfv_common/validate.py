#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import uuid


def valid_uuid_str(uuid_str, version=4):
    """
    Returns true if uuid string given is a valid uuid
    """
    try:
        uuid.UUID(uuid_str, version=version)

    except ValueError:
        return False

    return True


def valid_uuid_hex(uuid_hex_str, version=4):
    """
    Returns true if uuid hex string given is a valid uuid
    """
    try:
        uuid_value = uuid.UUID(uuid_hex_str, version=version)

    except ValueError:
        return False

    # Verify that the uuid_hex_str was not converted into a valid uuid.  This
    # is possible when the uuid_hex_str is a valid hex string but not a valid
    # uuid.  The uuid.UUID constructor will auto correct.
    return uuid_value.hex == uuid_hex_str


def valid_bool(boolean_str):
    """
    Returns true if string given is a valid boolean
    """
    if boolean_str.lower() in ['true', '1', 'false', '0']:
        return True
    return False


def valid_integer(integer_str):
    """
    Returns true if string given is a valid integer
    """
    try:
        int(integer_str)

    except ValueError:
        return False

    return True
