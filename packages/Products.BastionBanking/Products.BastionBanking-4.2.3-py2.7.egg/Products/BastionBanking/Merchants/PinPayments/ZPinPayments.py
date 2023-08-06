#
#    Copyright (C) 2013-2014  Corporation of Balclutha. All rights Reserved.
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

import json, logging
from DateTime import DateTime
import AccessControl
from AccessControl.Permissions import view
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import returncode
from Products.BastionBanking.interfaces.BastionMerchantInterface import IBastionMerchant
from Products.BastionBanking.BastionPayment import BastionPayment
from Products.BastionBanking.Exceptions import BankingException, ProcessingFailure
from Products.BastionBanking.Permissions import operate_bastionbanking
from Products.BastionBanking.ConnectionMgr import Transport
from Products.BastionBanking.ZCreditCard import ZCreditCard
from Products.BastionBanking.ZCurrency import ZCurrency
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

from zope.interface import implements

logger = logging.getLogger('BastionBanking.ZPinPayments')


#
# PinPayments config constants
#
PINPAYMENTS_SUPPORTED_CURRENCIES = ('AUD', 'CAD', 'EUR', 'GBP', 'HKD', 'JPY', 'NZD', 'SGD', 'USD')
PINPAYMENTS_URL = 'https://api.pin.net.au'
PINPAYMENTS_SANDBOX_URL = 'https://test-api.pin.net.au'

#
# our form widget ...
#
form = \
"""
<tal:block metal:define-macro="pay">
<img src="" valign="bottom"
     tal:attributes="src string:${request/BASEPATH1}/misc_/BastionBanking/pinpayments.gif"/>&nbsp;&nbsp;
<span class="form-label">Number</span>&nbsp;
<input type="text" size="16" name="cc_number">&nbsp;&nbsp;
<span class="form-label">Expires</span>&nbsp;
<select name="cc_year" tal:define="year python: DateTime().year()">
    <option tal:repeat="yy python: range(0, 4)" tal:content="python: year + yy"/>
</select>
<strong>&nbsp;/&nbsp;</strong>
<select name="cc_month">
    <option tal:repeat="mm python: range(1, 13)" tal:content="python: '%02d' % mm"/>
</select>
</tal:block>
"""

class ZPinPayments(ObjectManager, PropertyManager, SimpleItem):
    """
    Zope-based PinPayments interface.
    """
    meta_type = 'ZPinPayments'
    implements(IBastionMerchant)

    __ac_permissions__ = ObjectManager.__ac_permissions__ + (
        (operate_bastionbanking, ('setPagination',)),
        ) + PropertyManager.__ac_permissions__ + SimpleItem.__ac_permissions__

    __allow_access_to_unprotected_subobjects__ = 1

    form_macro = 'pinpayments'
    debuglevel = 1
    pagination = 1

    manage_options = (
        {'label':'Configuration', 'action':'manage_propertiesForm'},
        {'label':'Advanced', 'action':'manage_main'},
        ) + SimpleItem.manage_options

    #
    # signatures are generated from the 'profile' in your account, then 'Request API credentials'
    #
    _properties = PropertyManager._properties + (
        {'id':'form_macro',    'type':'string',    'mode':'r',},
        {'id':'key',           'type':'string',    'mode':'w',},
        {'id':'secret',        'type':'string',    'mode':'w',},
        {'id':'test_key',      'type':'string',    'mode':'w',},
        {'id':'test_secret',   'type':'string',    'mode':'w',},
        {'id':'pagination',    'type':'string',    'mode':'w',},
        {'id':'debuglevel',    'type':'int',       'mode':'w',},
        )

    def __init__(self, id, key='', secret='', test_key='',test_secret=''):
        self.id = id
        self.title = self.meta_type
        self.key = key
        self.secret = secret
        self.test_key = test_key
        self.test_secret = test_secret
        self._setObject('widget', ZopePageTemplate('widget', form))
 
    def _url(self):
        return self.aq_parent.mode == 'live' and PINPAYMENTS_URL or PINPAYMENTS_SANDBOX_URL

    def _secret(self):
        return self.aq_parent.mode == 'live' and self.secret or self.test_secret

    def supportedCurrencies(self):
        return PINPAYMENTS_SUPPORTED_CURRENCIES

    def serviceUrl(self):
        return "http://pin.net.au"

    def serviceLogo(self):
        return "/misc_/BastionBanking/pinpayments_logo.gif"

    def setPagination(self):
        """
        go get the next transaction id and set it
        """
        conn = Transport('%s/1/charges' % self._url(), self._secret())
        response, data = conn(headers={'Content-type':'application/json; charset=utf-8'}, action='GET')
        results = json.loads(data)
        self.pagination = results['pagination']['current']

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        return a BastionPayment - based upon us knowing what we've stuck in the form ...
        """
        payee = ZCreditCard(REQUEST['card']['number'],
                            DateTime('%s/%s/01' % (REQUEST['card']['year'], REQUEST['card']['month'])),
                            '',
                            REQUEST['card']['name'])
                                     
        return BastionPayment(id, payee, amount, ref)
    
    def _pay(self, payment, return_url, REQUEST=None):
        """
        """
        if REQUEST is None:
            REQUEST = self.REQUEST

        payee = self._payee(REQUEST)

        payee.update({'amount': payment.amount.cents(),
                      'currency': payment.amount.currency(),
                      'description': payment.reference,
                      'ip_address': REQUEST['REMOTE_ADDR']})

        if self.debuglevel:
            logger.info(payee)

        url = '%s/%i/charges' % (self._url(), self.pagination)
        conn = Transport(url, self._secret())

        response, data = conn(json.dumps(payee), {'Content-type':'application/json; charset=utf-8'})
        results = json.loads(data)

        if self.debuglevel:
            logger.info(response)
            logger.info(results)

        if response.status >= 400:
            # TODO - map all these to error field status messages ...
            logger.error(response.reason)
            errors = {}
            for error in results['messages']:
                errors[error['param'].replace('.', '').replace('_', '')] = error['message']
            raise ProcessingFailure(response.reason, errors)
            
        if results.get('pagination',{}).has_key('next'):
            self.pagination = results['pagination']['next']

        if not results['response'].has_key('token'):
            raise BankingException, (response, results)

        token = results['response']['token']
        payment.setRemoteRef(token)

        rc = returncode.returncode(token, payment.amount, 0, 0, 'PinPayments', data)
        return rc, ''

    def _payee(self, REQUEST):
        """
        return a structure that can be deblocked from REQUEST and re-rendered by form-macro and
        an id, unique across all kinds of payees, and that's checkId-friendly
        """
        payee = {'email': REQUEST.get('email', '')}

        card = {}
        for k in ('number', 'cvc', 'name'):
            card[k] = REQUEST['card'][k]
        for addr in ('line1', 'line2', 'city', 'postcode', 'state', 'country'):
            if REQUEST['card'].has_key('address_%s' % addr):
                card['address_%s' % addr] = REQUEST['card']['address_%s' % addr]
        card['expiry_year'] = REQUEST['card']['year']
        card['expiry_month'] = REQUEST['card']['month']

        payee['card'] = card

        return payee
    
    def _refund(self, payment, REQUEST=None):
        """
        we're doing full refunds - or nothing ...
        """
        token = pmt.getRemoteRef()
        conn = Transport('%s/%i/charges/%s/refunds' % (self._url(), self.pagination, token), self._secret())
        response, data = conn(headers={'Content-type':'application/json; charset=utf-8'}, action='POST')
        results = json.loads(data)

        results = response['response']

        if results.get('pagination',{}).has_key('next'):
            self.pagination = results['pagination']['next']

        return returncode.returncode(results['token'],
                                     payment.amount,
                                     0, results['success'] and OK or ERROR,
                                     results.get('error_message', None) or results['success_message'],
                                     data)

    def _reconcile(self, payment, REQUEST=None):
        """
        go complete payment on PinPayments side (if necessary) 
        """
        results = self.getTransaction(payment)

        return results.get('amount','') == str(payment.amount.cents()) and \
                results.get('currency', '') == payment.amount.currency() and \
                results.get('success', False)
                
    def getTransaction(self, pmt):
        """
        returns PinPayments's transaction info on the payment.
        """
        token = pmt.getRemoteRef()
        if token:
            conn = Transport('%s/%i/charges/%s' % (self._url(), self.pagination, token), self._secret())
            response, data = conn(headers={'Content-type':'application/json; charset=utf-8'}, action='GET')
            results = json.loads(data)
            return results['response']
        return {}

    def transactionFee(self, amount):
        """
        """
        # TODO - currency conversion??
        return ZCurrency('AUD 0.30') + amount * 0.03

AccessControl.class_init.InitializeClass(ZPinPayments)
