#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Tests for Cli module
"""

import unittest
import argparse

import mock
from croutera.models.routers import Routers
from croutera.exceptions import ModelNotFoundError

class RoutersTest(unittest.TestCase):

    def setUp(self):
        self.model1 = StubRouter
        self.model2 = mock.Mock
        self.model3 = mock.Mock
        self.model4 = mock.Mock
        self.models = {
           'manufacturer' : {
                'model1' : self.model1,
                'model2' : self.model2
           },
           'manufacturer2' : {
                'model3' : self.model3,
                'model4' : self.model4
           }
        }
        Routers.MANUFACTURER_MODELS = self.models

    def test_it_returns_all_models_from_manufacturer(self):
        self.assertEqual(self.models.get('manufacturer'),
                         Routers.from_manufacturer('manufacturer'))

    def test_it_returns_model_from_manufacturer(self):
        model = Routers.get('manufacturer', 'model1')
        self.assertIsInstance(model, StubRouter)

    def test_it_raise_model_not_found_error(self):
        self.assertRaises(ModelNotFoundError, Routers.get, 'manufacturer', 'model_invalid')

    def test_it_returns_sorted_models_available(self):
        self.assertEqual(Routers.list(), [
                                            'manufacturer-model1',
                                            'manufacturer-model2',
                                            'manufacturer2-model3',
                                            'manufacturer2-model4'
                                        ])


class StubRouter():
    pass
