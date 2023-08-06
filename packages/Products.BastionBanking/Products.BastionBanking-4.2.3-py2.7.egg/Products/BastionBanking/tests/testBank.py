#    Copyright (C) 2004  Corporation of Balclutha and contributors.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Testing import ZopeTestCase
from Products.PloneTestCase.PloneTestCase import PloneTestCase
ZopeTestCase.installProduct('BastionBanking')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

from ..config import BANKTOOL

class TestBastionBanking(PloneTestCase):

    def testCreation(self):
        self.app.manage_addProduct['BastionBanking'].manage_addBastionBankService('ManualPayment')
        self.failUnless(getattr(self.app, BANKTOOL, None))

from unittest import TestSuite, makeSuite

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBastionBanking))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
