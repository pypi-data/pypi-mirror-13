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

from zope.interface import Interface

class IMerchantTool(Interface):
    """
    A Merchant tool - control and manage merchant payments
    """
    def supportedCurrencies():
        """
        """

    def manage_payTransaction(txn, reference='', payee=None):
        """
        """

    def manage_refund(payment):
        """
        """

    def manage_reconcile(payment):
        """
        """

    def manage_accept(payment):
        """
        if this payment has been accepted, then post the transaction associated with it
        """

    def manage_reject(payment):
        """
        if this payment is not successful, then cancel the transaction associated with it
        """


class IBastionMerchant(Interface):
    """
    All Bank implementaions must support these functions ...
    """
    def __init__(id):
        """
        a default constructor is necessary ...
        """
        
    def supportedCurrencies():
	"""
	return a tuple of the currency codes supported by the underlying transport
	"""

    def serviceLogo():
        """
        the logo of the service to display on forms
        """

    def serviceUrl():
        """
        the url of the service, for legitimacy/info on forms
        """

    def _generateBastionPayment(id, amount, ref='', REQUEST={}):
        """
        take whatever was in the form and return a BastionPayment, with whatever's
        appropriate as payee

        not all merchant transactions are against credit cards, this allows us to
        pass an agreed format between function calls
        """
        
    def _pay(payee, amount, REQUEST=None):
        """
        returns returncode, redirect_url
        
        take client's credit card details and transact against it

        all parameters are passed in the request, allowing variable parameters ...

        this is a private function and should be called by BastionMerchantService (or
        some other function that has verified the input parameters)

        the redirect_url should be '' for gateways that don't hijack your customer
        """

    def _refund(payee, amount, ref, REQUEST=None):
        """
        returns returncode
        
        take client's credit card details and transact against it

        all parameters are passed in the request, allowing variable parameters ...

        this is a private function and should be called by BastionMerchantService (or
        some other function that has verified the input parameters)
        """

    def widget():
        """
        returns the form elements needed to make a payment for ZMI
        """

    def getTransaction(pmt):
        """
        returns a dict of details about the payment held by the provider
        """

    def merchantAccount(Ledger):
        """
        get the bank account associated with the merchant from the ledger (should
        be identified by a tag of the merchant service name
        """

    def merchantFee(amount):
        """
        return the merchant charge for processing the amount
        """
