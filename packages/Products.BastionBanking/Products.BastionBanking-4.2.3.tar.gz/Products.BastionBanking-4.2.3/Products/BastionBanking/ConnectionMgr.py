#
#    Copyright (c) 2004-2013, Corporation of Balclutha.
#
#    Please report any bugs or errors in this program to our bugtracker
#    at http://www.last-bastion.net/HelpDesk
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
#
import os
from httplib2 import Http, ProxyInfo, BasicAuthentication
from httplib2.socks import PROXY_TYPE_HTTP
from urlparse import urlparse
from urllib import urlencode
from threading import Lock

# this is for easy manipulation of headers and future extensibility
HEADERS = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept-Encoding":"identity",
    "Connection":"close",
    "keep-alive": '0',
    "User-Agent": 'BastionBanking'
    }

class Transport:
    """
    Python's httplib SSL layer is generally fucked, so we're providing a wrapper
    for it here.
    """
    _lock = Lock()

    def __init__(self, url, user='', password='', timeout=30):
        '''
        setup a request to a URL.  If user/password supplied, then set up
        basic http authentication headers
        '''
        self.url = url
        self.headers = dict(HEADERS)

        proto = urlparse(url)[0]

        proxyinfo = None
        proxy = '%s_proxy' % proto

        # TODO - this could be much smarter - checking against NO_PROXY etc, but that
        # would require netmask matching and more guestimating what to do ...
        if os.environ.has_key(proxy):
            pproto, phost, directory, params, query, frag = urlparse(os.environ[proxy])
            if phost.find('@') != -1:
                pcreds, phost = phost.split('@')
                puser, ppwd = pcreds.split(':')
            else:
                puser = ppwd = None
            if phost.find(':') != -1:
                phost,pport = phost.split(':')
            elif pproto == 'https':
                pport = '443'
            else:
                pport = '80'
            if puser and ppwd:
                proxyinfo = ProxyInfo(PROXY_TYPE_HTTP, phost, int(pport), proxy_user=puser, proxy_pass=ppwd)
            else:
                proxyinfo = ProxyInfo(PROXY_TYPE_HTTP, phost, int(pport))

        assert proto in ('http', 'https'), 'Unsupported Protocol: %s' % proto

        # note password *is* optional
        self.auth = BasicAuthentication((user, password), None, url, None, None, None, None)

        # simply ignore peer verification for now - we use http auth ;)
        self._v_conn = conn = Http(timeout=timeout, 
                                   proxy_info=proxyinfo, 
                                   disable_ssl_certificate_validation=True)

        
    def __call__(self, body='', headers={}, action="POST"):
        """
        make the request, returns the response packet contents, and response code as
        a tuple
        """
        # TODO - use a structure with case-insensitive keys
        req_hdrs = self.headers
        req_hdrs.update(headers)

        try:
            self._lock.acquire()

            self.auth and self.auth.request(None, None, req_hdrs, None)

            response, data = self._v_conn.request(self.url, 
                                                  method=action, 
                                                  body=body,
                                                  headers=req_hdrs)

            return (response, data)
        finally:
            self._lock.release()

    def __del__(self):
        try:
            self._v_conn.close()
        except:
            pass
