#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.database import model

from nfv_vim.database._database import database_get


def database_image_add(image_obj):
    """
    Add an image object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Image)
    query = query.filter(model.Image.uuid == image_obj.uuid)
    image = query.first()
    if not image:
        image = model.Image()
        image.uuid = image_obj.uuid
        image.name = image_obj.name
        image.description = image_obj.description
        image.avail_status = json.dumps(image_obj.avail_status)
        image.action = image_obj.action
        image.container_format = image_obj.container_format
        image.disk_format = image_obj.disk_format
        image.min_disk_size_gb = image_obj.min_disk_size_gb
        image.min_memory_size_mb = image_obj.min_memory_size_mb
        image.visibility = image_obj.visibility
        image.protected = image_obj.protected
        image.properties = json.dumps(image_obj.properties)
        image.nfvi_image_data = json.dumps(image_obj.nfvi_image.as_dict())
        session.add(image)
    else:
        image.description = image_obj.description
        image.avail_status = json.dumps(image_obj.avail_status)
        image.action = image_obj.action
        image.min_disk_size_gb = image_obj.min_disk_size_gb
        image.min_memory_size_mb = image_obj.min_memory_size_mb
        image.visibility = image_obj.visibility
        image.protected = image_obj.protected
        image.properties = json.dumps(image_obj.properties)
        image.nfvi_image_data = json.dumps(image_obj.nfvi_image.as_dict())
    db.commit()


def database_image_delete(image_uuid):
    """
    Delete an image object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Image)
    query.filter(model.Image.uuid == image_uuid).delete()
    session.commit()


def database_image_get_list():
    """
    Fetch all the image objects from the database
    """
    db = database_get()

    session = db.session()
    query = session.query(model.Image)

    image_objs = list()
    for image in query.all():
        nfvi_image_data = json.loads(image.nfvi_image_data)
        nfvi_image = nfvi.objects.v1.Image(nfvi_image_data['uuid'],
                                           nfvi_image_data['name'],
                                           nfvi_image_data['description'],
                                           nfvi_image_data['avail_status'],
                                           nfvi_image_data['action'],
                                           nfvi_image_data['container_format'],
                                           nfvi_image_data['disk_format'],
                                           nfvi_image_data['min_disk_size_gb'],
                                           nfvi_image_data['min_memory_size_mb'],
                                           nfvi_image_data['visibility'],
                                           nfvi_image_data['protected'],
                                           nfvi_image_data['properties'])
        image_obj = objects.Image(nfvi_image)
        image_objs.append(image_obj)
    return image_objs
