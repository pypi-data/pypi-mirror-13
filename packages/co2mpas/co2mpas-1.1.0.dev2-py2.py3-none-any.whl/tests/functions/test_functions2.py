#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import doctest
import unittest

from co2mpas.functions.physical.constants import NEDC

# class TestDoctest(unittest.TestCase):
#     def runTest(self):
#         import co2mpas.functions.physical.gear_box as mld
#
#         failure_count, test_count = doctest.testmod(
#             mld, optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
#         )
#         self.assertGreaterEqual(test_count, 0, (failure_count, test_count))
#         self.assertEqual(failure_count, 0, (failure_count, test_count))


class TNEDC(unittest.TestCase):

    def test_NEDC_length(self):
        fun = calculate_gear_box_efficiencies_torques_temperatures

        a = (self.wp, self.es, self.ws, self.tgb, self.pa, self.gbc, self.ts,
             self.Tr, self.st, self.g, self.gbr)
        res = fun(*a)
        v = np.zeros(self.g.shape)
        self.assertTrue(np.allclose(res[0], v + 1, 0, 0.001))
        self.assertTrue(np.allclose(res[1], self.tgb, 0, 0.001))
        self.assertTrue(np.allclose(res[2], v + self.st, 0, 0.001))
