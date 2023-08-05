"""SAML 2.0 client bindings module implements SOAP binding for attribute query

NERC DataGrid Project
"""
__author__ = "P J Kershaw"
__date__ = "02/09/09"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from urlparse import urlparse
import logging
log = logging.getLogger(__name__)

try:
    from ndg.httpsclient.https import HTTPSContextHandler as HTTPSHandler_
    
except ImportError:
    from M2Crypto.m2urllib2 import HTTPSHandler as HTTPSHandler_

from ndg.saml.saml2.core import AttributeQuery
from ndg.saml.saml2.binding.soap.client.subjectquery import (
                                                    SubjectQuerySOAPBinding,
                                                    SubjectQueryResponseError)

# Prevent whole module breaking if this is not available - it's only needed for
# AttributeQuerySslSOAPBinding
try:
    from ndg.saml.utils.pyopenssl import SSLContextProxy as SSLContextProxy_
    _sslContextProxySupport = True
    
except ImportError:
    try:
        from ndg.saml.utils.m2crypto import SSLContextProxy as SSLContextProxy_
        _sslContextProxySupport = True
        
    except ImportError:
        _sslContextProxySupport = False


class AttributeQueryResponseError(SubjectQueryResponseError):
    """SAML Response error from Attribute Query"""
    

class AttributeQuerySOAPBinding(SubjectQuerySOAPBinding): 
    """SAML Attribute Query SOAP Binding
    """
    SERIALISE_KW = 'serialise'
    DESERIALISE_KW = 'deserialise'
    QUERY_TYPE = AttributeQuery

    __slots__ = ()
    
    def __init__(self, **kw):
        '''Create SOAP Client for SAML Attribute Query'''
        
        # Default to ElementTree based serialisation/deserialisation
        if AttributeQuerySOAPBinding.SERIALISE_KW not in kw:
            from ndg.saml.xml.etree import AttributeQueryElementTree
            kw[AttributeQuerySOAPBinding.SERIALISE_KW
               ] = AttributeQueryElementTree.toXML
               
        if AttributeQuerySOAPBinding.DESERIALISE_KW not in kw:
            from ndg.saml.xml.etree import ResponseElementTree
            kw[AttributeQuerySOAPBinding.DESERIALISE_KW
               ] = ResponseElementTree.fromXML

        super(AttributeQuerySOAPBinding, self).__init__(**kw)
        
    def __setattr__(self, name, value):
        """Enable setting of SSLContextProxy attributes as if they were 
        attributes of this class.  This is intended as a convenience for 
        making settings parameters read from a config file
        """
        super(AttributeQuerySOAPBinding, self).__setattr__(name, value)

    
class AttributeQuerySslSOAPBinding(AttributeQuerySOAPBinding):
    """Specialisation of AttributeQuerySOAPbinding taking in the setting of
    SSL parameters for mutual authentication
    """
    SSL_CONTEXT_PROXY_SUPPORT = _sslContextProxySupport
    __slots__ = ('__sslCtxProxy',)
    
    def __init__(self, **kw):
        if not AttributeQuerySslSOAPBinding.SSL_CONTEXT_PROXY_SUPPORT:
            raise ImportError("ndg.saml.utils.m2crypto import "
                              "failed - missing M2Crypto package?")
        
        # Miss out default HTTPSHandler and set in send() instead
        if 'handlers' in kw:
            raise TypeError("__init__() got an unexpected keyword argument "
                            "'handlers'")
            
        super(AttributeQuerySslSOAPBinding, self).__init__(handlers=(), **kw)
        self.__sslCtxProxy = SSLContextProxy_()

    def send(self, query, **kw):
        """Override base class implementation to pass explicit SSL Context
        """
        if 'uri' in kw:
            parsed_url = urlparse(kw['uri'])
            self.sslCtxProxy.ssl_valid_hostname = parsed_url.netloc.split(':'
                                                                          )[0]
            
        httpsHandler = HTTPSHandler_(ssl_context=self.sslCtxProxy())
        self.client.openerDirector.add_handler(httpsHandler)
        return super(AttributeQuerySslSOAPBinding, self).send(query, **kw)
            
    def _getSslCtxProxy(self):
        return self.__sslCtxProxy
    
    def _setSslCtxProxy(self, value):
        if not isinstance(value, SSLContextProxy_):
            raise TypeError('Expecting %r type for "sslCtxProxy attribute; got '
                            '%r' % type(value))
            
        self.__sslCtxProxy = value
            
    sslCtxProxy = property(fget=_getSslCtxProxy, fset=_setSslCtxProxy,
                           doc="SSL Context Proxy object used for setting up "
                               "an SSL Context for queries")
    
    def __setattr__(self, name, value):
        """Enable setting of SSLContextProxy attributes as if they were 
        attributes of this class.  This is intended as a convenience for 
        making settings parameters read from a config file
        """
        try:
            super(AttributeQuerySslSOAPBinding, self).__setattr__(name, value)
            
        except AttributeError, e:
            # Coerce into setting SSL Context Proxy attributes
            try:
                setattr(self.sslCtxProxy, name, value)
            except Exception:
                raise e
