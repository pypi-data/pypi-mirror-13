# -*- coding: utf-8 -*-

from django.http import HttpRequest
from django.test import TestCase


class ContactTestCase(TestCase):
    """
    Contact Test
    """
    def test_manager(self):
        self.assertEquals(1, 1)
