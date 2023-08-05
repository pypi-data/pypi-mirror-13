# Copyright (c) 2016 LOGILAB S.A. (Paris, FRANCE).
#
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

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
    """Automatic tests value generator for the Email entity

    This is required since the 'headers' attribute should be plain
    ascii only
    """
    def generate_Email_headers(self, entity, index):
        return headers
