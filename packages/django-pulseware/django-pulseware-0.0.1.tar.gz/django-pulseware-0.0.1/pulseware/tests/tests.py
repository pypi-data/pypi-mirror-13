# -*- coding: utf-8 -*-

from django.http import HttpRequest
from django.test import TestCase


class HealthTestCase(TestCase):
    """
    Heath Test
    """

    def test_meta_none(self):
        self.assertEqual(1, 1)
