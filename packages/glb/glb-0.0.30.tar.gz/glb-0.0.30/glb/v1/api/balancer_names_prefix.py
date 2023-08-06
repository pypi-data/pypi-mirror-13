# -*- coding: utf-8 -*-

from . import Resource
from glb.models.balancer import Balancer as BalancerModel


class BalancerNamesPrefix(Resource):

    def get(self, prefix):
        all_obj_names = BalancerModel.retrieve_all_obj_ids()
        prefixed_names = [b_name for b_name in all_obj_names
                          if b_name.startswith(prefix)]
        return prefixed_names, 200, None
