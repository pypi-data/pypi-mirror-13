"""automatic tests for email views"""

from cubicweb.devtools.testlib import AutomaticWebTest
from cubicweb.devtools.fill import ValueGenerator


headers = u'''\
Return-Path: <python-projects-bounces@lists.logilab.org>
From: Benjamin Niemann <pink@odahoda.de>
To: python-projects@logilab.org
Subject: Re: [Python-projects] Pylint: Disable-msg for a block or statement?
Date: Tue, 4 Apr 2006 10:16:04 +0200
Message-Id: <200604041016.05182.pink@odahoda.de>
Sender: python-projects-bounces@lists.logilab.org

Some content'''

class EmailValueGenerator(ValueGenerator):

    def generate_Email_headers(self, entity, index):
        return headers


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Email', 'EmailPart', 'EmailThread'))

    def list_startup_views(self):
        return ()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
