#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from leryan.types import ObjectDict

class TestObjectDict(unittest.TestCase):
    def test_0010_empty_rule(self):
        r = ObjectDict({})
        self.assertEqual(r, {})

    def test_0011_simple_rule(self):
        r = ObjectDict({'simple':'rule'})
        self.assertEqual(r, {'simple':'rule'})

    def test_0012_nested_rule(self):
        r = ObjectDict({'nested':{'rule':', yepman'}})
        self.assertEqual(r, {'nested':{'rule':', yepman'}})

    def test_0020_add_by_attribute(self):
        r = ObjectDict({})
        setattr(r, 'add_attr', 'added_attr')
        self.assertEqual(r.add_attr, 'added_attr')

    def test_0021_add_by_key(self):
        r = ObjectDict({})
        r['add_attr'] = 'added_attr'
        self.assertEqual(r['add_attr'], 'added_attr')

    def test_0030_add_by_attr_access_by_key(self):
        r = ObjectDict({})
        setattr(r, 'add_attr', 'added_attr')
        self.assertEqual(r['add_attr'], 'added_attr')

    def test_0031_add_by_key_acces_by_attr(self):
        r = ObjectDict({})
        r['add_attr'] = 'added_attr'
        self.assertEqual(r.add_attr, 'added_attr')

    def test_0040_del_by_key_access_by_key_and_attr(self):
        r = ObjectDict({'key':'value'})
        del r['key']

        self.assertRaises(KeyError, r.__getitem__, 'key')
        self.assertRaises(AttributeError, r.__getattr__, 'key')

    def test_0041_del_by_attr_access_by_key_and_attr(self):
        r = ObjectDict({'key':'value'})
        delattr(r, 'key')

        self.assertRaises(KeyError, r.__getitem__, 'key')
        self.assertRaises(AttributeError, r.__getattr__, 'key')

    def test_0050_init_and_access_nested(self):
        r = ObjectDict({'root':{'sub1':{'sub2':'value'}}})

        self.assertEqual(r.root.sub1.sub2, 'value')

    def test_0060_set_nested_after_and_access(self):
        r = ObjectDict({})
        r['add_nested_attr'] = {'nested':{'attr':'value'}}

        self.assertEqual(r.add_nested_attr.nested.attr, 'value')
        self.assertEqual(r.add_nested_attr['nested'].attr, 'value')
        self.assertEqual(r['add_nested_attr'].nested['attr'], 'value')
        self.assertEqual(r['add_nested_attr']['nested']['attr'], 'value')

if __name__ == '__main__':
    unittest.main()

