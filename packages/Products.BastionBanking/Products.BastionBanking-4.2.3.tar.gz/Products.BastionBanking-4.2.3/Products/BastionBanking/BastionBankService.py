#
#    Copyright (C) 2003-2013  Corporation of Balclutha and contributors.
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

# import stuff
import AccessControl
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from OFS.Folder import Folder
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from BastionBankLog import BastionBankServiceLog
from config import BANKTOOL
import returncode
from ZReturnCode import ZReturnCode
from PortalContent import PortalContent
from BastionPayee import PayeeSupport
from Permissions import securityPolicy, operate_bastionbanking

manage_addBastionBankServiceForm = PageTemplateFile('zpt/add_bank', globals()) 
def manage_addBastionBankService(self, service, title='', id=BANKTOOL, REQUEST=None):
    """ """
    #
    # new up a service ...
    #
    try:
        exec('from Products.BastionBanking.Banks.%s.%s import %s' % (service, service, service))
        self._setObject(id,
                        BastionBankService(id,
                                           title,
                                           eval('''%s()'''% service ) ))

    except:
        raise
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' % (REQUEST['URL3'], id))
    

class ServicesFolder(Folder):
    """
    house our services ...
    """
    meta_type = 'ServicesFolder'

    def all_meta_types(self):
        return []

    def __init__(self, id, title='ServicesFolder'):
        self.id = id
        self.title = title

AccessControl.class_init.InitializeClass(ServicesFolder)


class BastionBankService(BTreeFolder2, ZCatalog, PropertyManager, PortalContent, PayeeSupport):
    """
    An encapsulation of a banking service provider.
    """
    meta_type = portal_type = 'BastionBankService'

    __ac_permissions__ = BTreeFolder2.__ac_permissions__ + ZCatalog.__ac_permissions__ + (
        (view_management_screens, ('manage_service',)),
        (operate_bastionbanking, ('manage_pay', )),
        ) + PropertyManager.__ac_permissions__ + PortalContent.__ac_permissions__ + PayeeSupport.__ac_permissions__

    manage_options = (
        { 'label':'Payees',     'action':'manage_payees', },
        { 'label':'Services',   'action':'manage_services' },
        { 'label':'View',       'action':'' },
        { 'label':'Log',        'action':'log/manage_workspace'},
        ) + ZCatalog.manage_options[1:]

    def all_meta_types(self):
   	return []
 
    def manage_services(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('services/manage_workspace')

    def __init__(self, id, title, imp):
        BTreeFolder2.__init__(self, id)
        ZCatalog.__init__(self, id)
        self.title = title
        self.services = ServicesFolder('services', 'Banking Service Provision')
        self.services._setObject(imp.id, imp)
        self.log = BastionBankServiceLog('log', 'Audit Log')
        self._setObject('banner', ZopePageTemplate('banner', ''))
        for id in ('meta_type', 'status', 'number'):
            self.addIndex(id, 'FieldIndex')
        self.addIndex('submitted', 'DateIndex')
        self.addIndex('reference', 'TextIndexNG3')
        self.addColumn('meta_type')

    def displayContentsTab(self):
        """
        we're not Plone-based ...
        """
        return False


    def manage_pay(self, account, amount, reference, REQUEST=None):
        """
        pass additional parameters in REQUEST ?? ...
        """
	# hmmm - ...
	service = self.services.objectValues()[0]
        rc = service.pay(amount, account, reference, REQUEST)
        
        if rc.severity <= returncode.OK:
            self.log.log(returncode.INFO, account.getId(), str(rc.__dict__))
        else:
            self.log.log(returncode.ERROR, account.getId(), str(rc.__dict__))

        return rc
       
AccessControl.class_init.InitializeClass(BastionBankService)


def addBastionBankService(ob, event):
    securityPolicy(bo)
    ob.log.manage_afterAdd(ob.log, ob)
        
