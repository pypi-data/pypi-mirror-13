#
#    Copyright (C) 2013  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, re
from AccessControl.Permissions import access_contents_information, view, view_management_screens
from Permissions import add_payee, operate_bastionbanking
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from PortalContent import PortalContent

cardnumber_re = re.compile(r'(\d{16})')

class BastionPayee(PortalContent):
    """
    Allow payee information to be stored/managed in Zope
    """
    meta_type = portal_type = 'BastionPayee'
    icon = 'misc_/BastionBanking/payee'

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (access_contents_information, ('setRequest', 'masked')),
        (operate_bastionbanking, ('edit',)),
        )

    _properties = PortalContent._properties + (
        {'id':'gateway',             'type':'string', 'mode':'r'},
        )

    def __init__(self, id, title, gateway, payee):
        self.id = id
        self.title = title
        self.gateway = gateway
        self.payee = payee
        
    # private - for indexing only
    def number(self):
        match = cardnumber_re.search(str(self.payee))
        if match:
            return match.groups()[0]
        raise AttributeError, 'number'

    def masked(self):
        """
        """
        try:
            number = self.number()
            return '%sXXXXXX%s' % (number[0:7], number[-4:])
        except:
            return 'XXXXXXXXXXXXXXXXXXXX'

    def setRequest(self, REQUEST=None):
        """
        shove payee details into REQUEST to display in forms
        """
        REQUEST = REQUEST or self.REQUEST
        for k, v in self.payee.items():
            REQUEST.set(k,v)

    def edit(self, REQUEST=None):
        """
        update payee details from REQUEST
        """
        service = self.aq_parent.service
        self.payee = service._payee(REQUEST or self.REQUEST)

AccessControl.class_init.InitializeClass(BastionPayee)


#class PayeeSupport(BTreeFolder2):
class PayeeSupport:
    """
    managing payees
    """
    __ac_permissions__ = (
        (add_payee, ('deletePayee', 'setPayee')),
        # getPayee is view so non-logged in users can make payments
        (view, ('getPayee',)),
        (view_management_screens, ('manage_payees', 'payeeIds', 'payeeValues', 'payeeResults')),
        )

    manage_payees = PageTemplateFile('zpt/payees', globals())

    def getPayee(self, context, gateway='', REQUEST=None):
        """
        pass in an object and gateway id, we'll return payee
        if you pass in a REQUEST, it'll pack the payee into this too
        """
        gateway = gateway or self.service.meta_type

        # only ZODB/content types implement UID ...
        try:
            pid = context.UID()
        except:
            #raise AttributeError, '%s: UID()' % context.__class__.__name__
            return None

        payee = self._getOb(pid, None)
        if payee and payee.meta_type == 'BastionPayee' and payee.gateway == gateway:
            if REQUEST:
                payee.setRequest(REQUEST)
            return payee

        return None

    def setPayee(self, context, gateway='', REQUEST=None):
        # TODO - find gateway, just assume it's the service()
        gateway = gateway or self.service.meta_type

        payee = self.service._payee(REQUEST or self.REQUEST)
        mypayee = self.getPayee(context, gateway)
        if mypayee:
            mypayee.payee = payee
        else:
            pid = context.UID()
            #raise AssertionError, (pid, context.__dict__)
            self._setObject(pid, BastionPayee(pid, context.Title(), gateway, payee))

    def deletePayee(self, context, gateway=''):
        payee = self.getPayee(context, gateway or self.service.meta_type)
        if payee:
            self._delObject(payee.getId())

    def payeeValues(self):
        return self.objectValues('BastionPayee')

    def payeeIds(self):
        return self.objectIds('BastionPayee')

    def payeeResults(self, REQUEST={}):
        return self.searchResults(REQUEST=REQUEST, meta_type='BastionPayee')

#AccessControl.class_init.InitializeClass(PayeeSupport)
