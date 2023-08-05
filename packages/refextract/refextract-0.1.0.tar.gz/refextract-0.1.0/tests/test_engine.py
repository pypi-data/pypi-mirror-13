# -*- coding: utf-8 -*-
#
# This file is part of refextract
# Copyright (C) 2016 CERN.
#
# refextract is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# refextract is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with refextract; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""The Refextract unit test suite"""

from refextract.references.engine import (
    parse_references,
)

from refextract.references.text import wash_and_repair_reference_line


def get_references(ref_line, override_kbs_files=None):
    ref_line = wash_and_repair_reference_line(ref_line)
    return parse_references([ref_line], override_kbs_files=override_kbs_files)


def test_month_with_year():
    ref_line = u"""[2] S. Weinberg, A Model of Leptons, Phys. Rev. Lett. 19 (Nov, 1967) 1264–1266."""
    res = get_references(ref_line)
    assert len(res['references']) == 1
    assert res['references'][0]['author'] == [u'S. Weinberg, A Model of Leptons']
    assert res['references'][0]['journal_page'] == [u'1264-1266']
    assert res['references'][0]['journal_reference'] == [u'Phys. Rev. Lett. 19 (1967) 1264-1266']
    assert res['references'][0]['journal_title'] == [u'Phys. Rev. Lett.']
    assert res['references'][0]['journal_volume'] == [u'19']
    assert res['references'][0]['journal_year'] == [u'1967']
    assert res['references'][0]['linemarker'] == [u'2']
    assert res['references'][0]['year'] == [u'1967']


def test_numeration_not_finding_year():
    ref_line = u"""[137] M. Papakyriacou, H. Mayer, C. Pypen, H. P. Jr., and S. Stanzl-Tschegg, “Inﬂuence of loading frequency on high cycle fatigue properties of b.c.c. and h.c.p. metals,” Materials Science and Engineering, vol. A308, pp. 143–152, 2001."""
    res = get_references(ref_line)
    assert len(res['references']) == 1
    assert res['references'][0]['author'] == [u'M. Papakyriacou, H. Mayer, C. Pypen, H. P. Jr., and S. Stanzl-Tschegg']
    assert res['references'][0]['journal_page'] == [u'143-152']
    assert res['references'][0]['journal_reference'] == [u'Mat.Sci.Eng. A308 (2001) 143-152']
    assert res['references'][0]['journal_title'] == [u'Mat.Sci.Eng.']
    assert res['references'][0]['journal_volume'] == [u'A308']
    assert res['references'][0]['journal_year'] == [u'2001']
    assert res['references'][0]['linemarker'] == [u'137']
    assert res['references'][0]['year'] == [u'2001']
    assert res['references'][0]['title'] == [u'Influence of loading frequency on high cycle fatigue properties of b.c.c. and h.c.p. metals']


def test_numeration_not_finding_year2():
    ref_line = u"""[138] Y.-B. Park, R. Mnig, and C. A. Volkert, “Frequency effect on thermal fatigue damage in Cu interconnects,” Thin Solid Films, vol. 515, pp. 3253– 3258, 2007."""
    res = get_references(ref_line)
    assert len(res['references']) == 1
    assert res['references'][0]['author'] == [u'Y.-B. Park, R. Mnig, and C. A. Volkert']
    assert res['references'][0]['journal_page'] == [u'3253-3258']
    assert res['references'][0]['journal_reference'] == [u'Thin Solid Films 515 (2007) 3253-3258']
    assert res['references'][0]['journal_title'] == [u'Thin Solid Films']
    assert res['references'][0]['journal_volume'] == [u'515']
    assert res['references'][0]['journal_year'] == [u'2007']
    assert res['references'][0]['linemarker'] == [u'138']
    assert res['references'][0]['year'] == [u'2007']
    assert res['references'][0]['title'] == [u'Frequency effect on thermal fatigue damage in Cu interconnects']


def test_extra_a_in_report_number():
    ref_line = u'[14] CMS Collaboration, CMS-PAS-HIG-12-002. CMS Collaboration, CMS-PAS-HIG-12-008. CMS Collaboration, CMS-PAS-HIG-12-022. ATLAS Collaboration, arXiv:1205.0701. ATLAS Collaboration, ATLAS-CONF-2012-078.'
    res = get_references(ref_line)
    assert len(res['references']) == 1
    assert res['references'][0]['collaboration'] == [
        u'CMS Collaboration',
        u'ATLAS Collaboration',
    ]
    assert res['references'][0]['reportnumber'] == [
        u'CMS-PAS-HIG-12-002',
        u'CMS-PAS-HIG-12-008',
        u'CMS-PAS-HIG-12-022',
        u'arXiv:1205.0701',
        u'ATLAS-CONF-2012-078',
    ]
    assert res['references'][0]['linemarker'] == [u'14']
