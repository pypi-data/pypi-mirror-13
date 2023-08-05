#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Models routers implementations
"""

import base64

from croutera.models.cisco import CiscoDPC3928S
from croutera.models.tplink import TplinkWR340, TplinkWR720N, tlwrbased
from croutera.models.dlink import DLinkDir610
from croutera.exceptions import ModelNotFoundError

class Routers(object):
    """ Provide Router.class instances """

    MANUFACTURER_MODELS = {
        'cisco' : {
            'dpc3928s' : CiscoDPC3928S
        },
        'dlink' : {
            'dir610' : DLinkDir610
        },
        'tplink' : {
            'wr340g' : TplinkWR340,
            'wr720n' : TplinkWR720N,
            'tl-wrbased': tlwrbased.TplinkTLWRBased
        }
    }

    @staticmethod
    def get(manufacturer, model):
        models = Routers.from_manufacturer(manufacturer)
        router = models.get(model)
        if router is None:
            raise ModelNotFoundError('Model not found for this manufacturer.')

        return router()

    @staticmethod
    def from_manufacturer(manufacturer):
        models = Routers.MANUFACTURER_MODELS.get(manufacturer)

        if models is None:
            raise ModelNotFoundError('Manufacturer not found.')

        return models

    @staticmethod
    def list():
        available = []
        manufacturers = Routers.MANUFACTURER_MODELS.keys()
        for man in manufacturers:
            models = Routers.MANUFACTURER_MODELS.get(man)
            for mdl in models:
                available.append("%s-%s" % (man, mdl))
        return sorted(available)
