#
# Copyright 2007-2013 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# Permission to use, copy, modify, and distribute this software
# and its documentation for any purpose whatsoever is strictly
# prohibited without prior written consent of Corporation of Balclutha.
# 
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import AccessControl
from Acquisition import aq_base
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.Archetypes import AmountField, AmountWidget

# stuff for our dummy archetype class
from Products.BastionBanking.config import PROJECTNAME
from Products.Archetypes.atapi import registerType, BaseContent, Schema
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFTestCase.ctc import setupCMFSite

# archetype test harness
try:
    from Products.Archetypes.tests.attestcase import ATTestCase
except KeyError:
    # hmmm - seems profile-Products.Archetypes:Archetypes_sampletypes isn't getting registered
    from Products.PloneTestCase.PloneTestCase import PloneTestCase as ATTestCase
from Products.Archetypes.tests.utils import PACKAGE_HOME
from Products.Archetypes.tests.utils import makeContent

class Dummy(BaseContent):
    schema = BaseContent.schema.copy() + Schema((
    AmountField('amount',
                required=False,
                searchable=True,
                #accessor='contact_email',
                write_permission = ModifyPortalContent,
                widget = AmountWidget(
    description = "Currency Amount",
    description_msgid = "help_value",
    label = "Economic Value",
    label_msgid = "label_Value",
    i18n_domain = "plone")),
    ))

    meta_type = portal_type = archetype_name = 'Dummy'

    immediate_view             = 'base'
    default_view               = 'base'

AccessControl.class_init.InitializeClass(Dummy)
registerType(Dummy, PROJECTNAME)

class TestArchetypes(ATTestCase):
    '''Tests our Archetypes widgets - well actually its completely broken because
    we somehow need to installProduct our little dummy class so as we can
    create objects...'''


    # Test the fixture ##############################################

    def XtestTest(self):
        """
        hmmm - do widget tests *really* work???   NO!!!!
        """
        self.loginAsPortalOwner()
        self.portal.createObject(type_name='Dummy', id='doc')
        doc = self.portal.doc
        
        field = doc.Schema()['amount']
        widget = field.widget
        form = {'amount':'USD 1.23'}
        expected = ZCurrency('USD 1.23')
        result = widget.process_form(doc, field, form)
        #self.assertEqual(expected, result[0])
        
    def XtestRendering(self):
        self.loginAsPortalOwner()
        self.portal.createObject(type_name='Dummy', id='doc')
        doc = self.portal.doc

         #Now render this doc in view and edit modes. If this works
        #then we have pretty decent assurance that things are working
        view = doc.base_view()
        edit = doc.base_edit()

from unittest import TestSuite, makeSuite

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestArchetypes))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

