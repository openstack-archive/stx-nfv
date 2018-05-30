#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import objects

import model
from _database import database_get


def database_tenant_add(tenant_obj):
    """
    Add a tenant object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Tenant)
    tenant = query.filter(model.Tenant.uuid == tenant_obj.uuid).first()
    if not tenant:
        tenant = model.Tenant()
        tenant.uuid = tenant_obj.uuid
        tenant.name = tenant_obj.name
        tenant.description = tenant_obj.description
        tenant.enabled = tenant_obj.enabled
        session.add(tenant)
    else:
        tenant.description = tenant_obj.description
        tenant.enabled = tenant_obj.enabled
    db.commit()


def database_tenant_delete(tenant_uuid):
    """
    Delete a tenant object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Tenant)
    query.filter(model.Tenant.uuid == tenant_uuid).delete()
    session.commit()


def database_tenant_get_list():
    """
    Fetch all the tenant objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Tenant)

    tenant_objs = list()
    for tenant in query.all():
        tenant_obj = objects.Tenant(tenant.uuid, tenant.name,
                                    tenant.description, tenant.enabled)
        tenant_objs.append(tenant_obj)
    return tenant_objs
