#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_vim import nfvi
from nfv_vim import objects

import model
from _database import database_get


def database_volume_add(volume_obj):
    """
    Add a volume object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Volume)
    query = query.filter(model.Volume.uuid == volume_obj.uuid)
    volume = query.first()
    if not volume:
        volume = model.Volume()
        volume.uuid = volume_obj.uuid
        volume.name = volume_obj.name
        volume.description = volume_obj.description
        volume.avail_status = json.dumps(volume_obj.avail_status)
        volume.action = volume_obj.action
        volume.size_gb = volume_obj.size_gb
        volume.bootable = volume_obj.bootable
        volume.encrypted = volume_obj.encrypted
        volume.image_uuid = volume_obj.image_uuid
        volume.nfvi_volume_data = json.dumps(volume_obj.nfvi_volume.as_dict())
        session.add(volume)
    else:
        volume.name = volume_obj.name
        volume.description = volume_obj.description
        volume.avail_status = json.dumps(volume_obj.avail_status)
        volume.action = volume_obj.action
        volume.size_gb = volume_obj.size_gb
        volume.bootable = volume_obj.bootable
        volume.encrypted = volume_obj.encrypted
        volume.image_uuid = volume_obj.image_uuid
        volume.nfvi_volume_data = json.dumps(volume_obj.nfvi_volume.as_dict())
    db.commit()


def database_volume_delete(volume_uuid):
    """
    Delete a volume object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Volume)
    query.filter(model.Volume.uuid == volume_uuid).delete()
    session.commit()


def database_volume_get_list():
    """
    Fetch all the volume objects from the database
    """
    db = database_get()

    session = db.session()
    query = session.query(model.Volume)

    volume_objs = list()
    for volume in query.all():
        nfvi_volume_data = json.loads(volume.nfvi_volume_data)
        nfvi_volume = nfvi.objects.v1.Volume(nfvi_volume_data['uuid'],
                                             nfvi_volume_data['name'],
                                             nfvi_volume_data['description'],
                                             nfvi_volume_data['avail_status'],
                                             nfvi_volume_data['action'],
                                             nfvi_volume_data['size_gb'],
                                             nfvi_volume_data['bootable'],
                                             nfvi_volume_data['encrypted'],
                                             nfvi_volume_data['image_uuid'])
        volume_obj = objects.Volume(nfvi_volume)
        volume_objs.append(volume_obj)
    return volume_objs


def database_volume_snapshot_add(volume_snapshot_obj):
    """
    Add a volume snapshot object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.VolumeSnapshot)
    query = query.filter(model.VolumeSnapshot.uuid == volume_snapshot_obj.uuid)
    volume_snapshot = query.first()
    if not volume_snapshot:
        volume_snapshot = model.VolumeSnapshot()
        volume_snapshot.uuid = volume_snapshot_obj.uuid
        volume_snapshot.name = volume_snapshot_obj.name
        volume_snapshot.description = volume_snapshot_obj.description
        volume_snapshot.size_gb = volume_snapshot_obj.size_gb
        volume_snapshot.volume_uuid = volume_snapshot_obj.volume_uuid
        volume_snapshot.nfvi_volume_snapshot_data = \
            json.dumps(volume_snapshot_obj.nfvi_volume_snapshot.as_dict())
        session.add(volume_snapshot)
    else:
        volume_snapshot.name = volume_snapshot_obj.name
        volume_snapshot.description = volume_snapshot_obj.description
        volume_snapshot.size_gb = volume_snapshot_obj.size_gb
        volume_snapshot.volume_uuid = volume_snapshot_obj.volume_uuid
        volume_snapshot.nfvi_volume_snapshot_data = \
            json.dumps(volume_snapshot_obj.nfvi_volume_snapshot.as_dict())
    db.commit()


def database_volume_snapshot_delete(volume_snapshot_uuid):
    """
    Delete a volume snapshot object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.VolumeSnapshot)
    query.filter(model.VolumeSnapshot.uuid == volume_snapshot_uuid).delete()
    session.commit()


def database_volume_snapshot_get_list():
    """
    Fetch all the volume snapshot objects from the database
    """
    db = database_get()

    session = db.session()
    query = session.query(model.VolumeSnapshot)

    volume_snapshot_objs = list()
    for volume_snapshot in query.all():
        nfvi_volume_snapshot_data = \
            json.loads(volume_snapshot.nfvi_volume_snapshot_data)
        nfvi_volume_snapshot = nfvi.objects.v1.VolumeSnapshot(
            nfvi_volume_snapshot_data['uuid'],
            nfvi_volume_snapshot_data['name'],
            nfvi_volume_snapshot_data['description'],
            nfvi_volume_snapshot_data['size_gb'],
            nfvi_volume_snapshot_data['volume_uuid'])
        volume_snapshot_obj = objects.VolumeSnapshot(nfvi_volume_snapshot)
        volume_snapshot_objs.append(volume_snapshot_obj)
    return volume_snapshot_objs
