#
#    Copyright (C) 2005-2013  Corporation of Balclutha. All rights Reserved.
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

#
#    The definitions of all exceptions thrown by this suite
#

class BankingException(Exception):
    """
    an exception within the BastionBanking suite
    """

class InvalidAmount(BankingException):
    """
    an amount is invalid eg zero (say), for the context it's being used
    """

class UnsupportedCurrency(BankingException):
    """
    We don't know about this currency type, you probably need a Tradeable entry
    to translate it into a base currency we can enact upon
    """
    pass

class CreditCardInvalid(BankingException):
    """
    Credit card number doesn't pass validation test
    """
    pass

class CreditCardExpired(BankingException):
    """
    Credit card has expired 
    """
    pass

class ProcessingFailure(BankingException):
    """
    Back office rejected our request
    """
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, error, messages={}):
        """
        messages is a hash of form-fields and their error messages
        """
        self.error = error
        self.messages = messages

    def __str__(self):
        return self.error
