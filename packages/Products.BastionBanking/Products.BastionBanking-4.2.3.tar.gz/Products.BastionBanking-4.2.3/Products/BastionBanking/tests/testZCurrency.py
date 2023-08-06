#
#    Copyright (C) 2008-2013  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os, sys

from Testing import ZopeTestCase

# register our converter
ZopeTestCase.installProduct('BastionBanking')

from Products.BastionBanking.ZCurrency import ZCurrency

class ZCurrencyTest(ZopeTestCase.ZopeTestCase):

    def testStringFirst(self):
        self.failUnless( ZCurrency('GBP', 12.34) )

    def testAmountFirst(self):
        self.failUnless( ZCurrency(-12.34, 'GBP') )

    def testString(self):
        self.failUnless( ZCurrency('GBP12.34') )

    def testStringGap(self):
        self.failUnless( ZCurrency('GBP -12.34') )

    def testStringSigns(self):
        self.failUnless( ZCurrency('-GBP 12.34') )
        self.failUnless( ZCurrency('+GBP 12.34') )
        self.assertEqual( ZCurrency('GBP 12.34'), ZCurrency('+GBP -12.34') )
        self.assertEqual( ZCurrency('GBP 12.34'), ZCurrency('+GBP +12.34') )
        self.assertEqual( ZCurrency('-GBP 12.34'), ZCurrency('GBP -12.34') )
        self.assertEqual( ZCurrency('-GBP 12.34'), ZCurrency('-GBP -12.34') )

    def testAdd(self):
        amt = ZCurrency('GBP12.34')
        self.assertEqual(amt+amt, ZCurrency('GBP24.68'))

    def testSub(self):
        amt = ZCurrency('GBP12.34')
        self.assertEqual(amt-amt, ZCurrency('GBP0.00'))

    def testMul(self):
        amt = ZCurrency('GBP12.34')
        self.assertEqual(amt*2, ZCurrency('GBP24.68'))

    def testEqualities(self):
        a =  ZCurrency('GBP12.34')
        b =  ZCurrency('GBP12.34')
        c =  -ZCurrency('GBP12.34')
        self.failUnless(a == b)
        self.failUnless(b != c)
        self.failIf(b == c)

    def testCurrencyProperty(self):
        # test our currency property type
        self.folder.manage_addProperty('amount', 'GBP24.78', 'currency')
        self.folder._updateProperty('amount', 'GBP10.00')
        self.failUnless(isinstance(self.folder.getProperty('amount'), ZCurrency))
        self.assertEqual(self.folder.getProperty('amount'), ZCurrency('GBP10.00'))

    def testWidgetMarshalling(self):
        currency = ZCurrency('GBP10.00')
        for qs  in ('amt:currency=GBP10.00',):
            env = {'SERVER_NAME': 'testingharness', 'SERVER_PORT': '80'}
            env['QUERY_STRING'] = qs
            from ZPublisher.HTTPRequest import HTTPRequest
            req = HTTPRequest(None, env, None)
            req.processInputs()
            # this is f**ked and we've only got a record instance which our __cmp__ function
            # happily considers a ZCurrency ...
            #print req.amt
            #self.failUnless(isinstance(req.amt, ZCurrency))
            self.assertEqual(currency, req.amt)
                                                                                        

from unittest import TestSuite, makeSuite
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ZCurrencyTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
