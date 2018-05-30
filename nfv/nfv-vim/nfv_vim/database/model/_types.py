#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from passlib.hash import sha512_crypt

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class Secret(str):
    """
    Secret
    """
    def __new__(cls, value, encrypt=True, salt=None, rounds=40000):
        if encrypt:
            value = sha512_crypt.encrypt(value, salt=salt, rounds=rounds)
        return str.__new__(cls, value)

    def __eq__(self, other):
        if isinstance(other, Secret):
            return str.__eq__(self, other)
        return sha512_crypt.verify(other, self)

    def __ne__(self, other):
        return not self.__eq__(other)


class SecretType(TypeDecorator):
    """
    Secret Database Type
    """
    impl = String(128)

    def process_bind_param(self, value, dialect):
        return Secret(value)

    def process_result_value(self, value, dialect):
        return Secret(value, encrypt=False)


class VNF_UUID(TypeDecorator):
    """
    VNF UUID Database Type
    """
    impl = String(64)  # Prefix string (28 characters) + uuid (36 characters)

    def process_bind_param(self, value, dialect):
        return "VNF-" + str(value)

    def process_result_value(self, value, dialect):
        return value[4:]
