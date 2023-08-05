# -*- coding:utf-8 -*-
import unittest

from afinder import afind


class AfinderTest(unittest.TestCase):

    def test_afind(self):
        class A(object):
            name = 'Kapor'
            attr = {
                'name': 'Hello kapor'
            }
            kapor = 'my name'

            class B(object):
                name = 'kapor'
            b_obj = B()
            age = 100

        self.assertEqual(len(afind(A(), 'name')), 4)
        self.assertEqual(len(afind(A(), 'kapor')), 4)
        self.assertEqual(len(afind(A(), '10')), 1)
