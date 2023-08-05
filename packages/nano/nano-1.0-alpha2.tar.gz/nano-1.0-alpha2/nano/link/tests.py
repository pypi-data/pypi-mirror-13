from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.test import TestCase

from nano.link.models import Link

class LinkTest(TestCase):

    def test_check(self):
        link = Link(uri='http://example.com/')
        linkcheck = link.verify()
        self.assertEqual(linkcheck, None)

    def test_str(self):
        link = Link(uri='http://example.com/')
        self.assertEqual(force_text(link), link.uri)
