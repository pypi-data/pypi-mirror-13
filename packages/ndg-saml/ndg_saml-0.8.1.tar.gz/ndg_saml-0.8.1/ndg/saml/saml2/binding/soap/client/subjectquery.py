"""SAML 2.0 bindings module implements SOAP binding for subject query

NERC DataGrid Project
"""
__author__ = "P J Kershaw"
__date__ = "12/02/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from ndg.saml.saml2.core import SubjectQuery
from ndg.saml.saml2.binding.soap.client import SOAPBindingInvalidResponse
from ndg.saml.saml2.binding.soap.client.requestbase import (
    RequestBaseSOAPBinding,)


class SubjectQueryResponseError(SOAPBindingInvalidResponse):
    """SAML Response error from Subject Query"""
    

class SubjectQuerySOAPBinding(RequestBaseSOAPBinding):
    """SAML Subject Query SOAP Binding
    """ 
    __PRIVATE_ATTR_PREFIX = "__"
    __slots__ = ()
    
    QUERY_TYPE = SubjectQuery
    
    def __init__(self, **kw):
        '''Create SOAP Client for a SAML Subject Query'''       
        super(SubjectQuerySOAPBinding, self).__init__(**kw)


