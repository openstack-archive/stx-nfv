#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan
from wsme import types as wsme_types


class Link(wsme_types.Base):
    """
    Representation of a Link using JSON Hyper-Schema
    """
    title = wsme_types.text
    rel = wsme_types.text
    href = wsme_types.text
    method = wsme_types.text
    type = wsme_types.text

    @classmethod
    def make_link(cls, rel, url, resource, resource_args=None,
                  title=wsme_types.Unset, method=wsme_types.Unset,
                  type=wsme_types.Unset):

        forwarded_proto = pecan.request.headers.get('X-Forwarded-Proto', '')
        if 'https' == forwarded_proto.lower():
            if url.startswith('http:'):
                url = url.replace('http', 'https', 1)

        if resource_args is None:
            resource_args = ''

        template = '%s/%s'
        template += '%s' if resource_args.startswith('?') else '/%s'

        return Link(title=title, rel=rel,
                    href=template % (url, resource, resource_args),
                    method=method, type=type)
