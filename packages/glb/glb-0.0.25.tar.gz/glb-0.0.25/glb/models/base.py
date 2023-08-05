# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glb.core.extensions import db


class CRUDMixin(object):

    @classmethod
    def create(cls, **kwargs):
        obj = cls()
        for k, v in kwargs.iteritems():
            setattr(obj, k, v)
        return obj

    @classmethod
    def save(cls, data):
        return db.save(cls.__prefix_key__, cls.__primary_key__, data)

    @classmethod
    def update(cls, obj_id, data):
        return db.update(cls.__prefix_key__, obj_id, data)

    @classmethod
    def delete(cls, obj_id):
        return db.delete_one(cls.__prefix_key__, obj_id)

    @classmethod
    def retrieve(cls, obj_id):
        rs = {}
        obj = db.fetch_one(cls.__prefix_key__, cls.__primary_key__, obj_id)
        if obj:
            rs = cls.create(**obj)
        return rs

    @classmethod
    def retrieve_list(cls):
        objs = db.fetch_all(cls.__prefix_key__, cls.__primary_key__)
        rs = [cls.create(**obj) for obj in objs]
        return rs

    @classmethod
    def retrieve_all_obj_ids(cls):
        return db.fetch_all_obj_ids(
            cls.__prefix_key__, cls.__primary_key__)


class Model(CRUDMixin, object):
    __abstract__ = True
