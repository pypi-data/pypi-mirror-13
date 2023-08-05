"""SAML 2.0 Utilities module for M2Crypto SSL functionality 

NDG SAML
"""
__author__ = "P J Kershaw"
__date__ = "29/05/15"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import os
import re
from abc import ABCMeta, abstractmethod
import logging

log = logging.getLogger(__name__)


class SSLContextProxyInterface(object):
    """Interface class for SSL proxy to allow interchange between PyOpenSSL and
    M2Crypto HTTPS libraries"""
    __metaclass__ = ABCMeta
    
    SSL_CERT_FILEPATH_OPTNAME = "sslCertFilePath"
    SSL_PRIKEY_FILEPATH_OPTNAME = "sslPrikeyFilePath"
    SSL_PRIKEY_PWD_OPTNAME = "sslPrikeyPwd"
    SSL_CACERT_FILEPATH_OPTNAME = "sslCACertFilePath"
    SSL_CACERT_DIRPATH_OPTNAME = "sslCACertDir"
    SSL_VALID_X509_SUBJ_NAMES_OPTNAME = "ssl_valid_x509_subj_names"
    SSL_VALID_HOST_NAME_OPTNAME = "ssl_valid_x509_subj_names"
    
    OPTNAMES = (
        SSL_CERT_FILEPATH_OPTNAME,
        SSL_PRIKEY_FILEPATH_OPTNAME,
        SSL_PRIKEY_PWD_OPTNAME,
        SSL_CACERT_FILEPATH_OPTNAME,
        SSL_CACERT_DIRPATH_OPTNAME,
        SSL_VALID_X509_SUBJ_NAMES_OPTNAME
    )
    
    __slots__ = (
        "_ssl_cert_filepath",
        "_ssl_prikey_filepath",
        "_ssl_prikey_pwd",
        "_ssl_cacert_filepath",
        "_ssl_ca_cert_dir",
        "_ssl_valid_hostname",
        "_ssl_valid_x509_subj_names"
    )
            
    VALID_DNS_PAT = re.compile(',\s*')

    def __init__(self):
        self._ssl_cert_filepath = None
        self._ssl_prikey_filepath = None
        self._ssl_prikey_pwd = None
        self._ssl_cacert_filepath = None
        self._ssl_ca_cert_dir = None
        self._ssl_valid_hostname = None
        self._ssl_valid_x509_subj_names = []
        
    @abstractmethod
    def __call__(self):
        """Create an SSL Context from this objects properties
        :type depth: int
        :param depth: max. depth of certificate to verify against
        :type kw: dict
        :param kw: SSL Context keyword arguments
        :rtype: SSL Context of wrapped class e.g. M2Crpyto.SSL.Context or
        OpenSSL.SSL.Context depending on the SSL library used in the implemented
        class
        @return SSL context object
        """
        
    def copy(self, sslCtxProxy):
        """Copy settings from another context object
        """
        if not isinstance(sslCtxProxy, SSLContextProxyInterface):
            raise TypeError('Expecting %r for copy method input object; '
                            'got %r' % (SSLContextProxyInterface, 
                                        type(sslCtxProxy)))
        
        for name in self.__class__.OPTNAMES:
            setattr(self, name, getattr(sslCtxProxy, name))
            
    @property
    def sslCertFilePath(self):
        return self._ssl_cert_filepath
    
    @sslCertFilePath.setter
    def sslCertFilePath(self, filePath):
        "Set X.509 cert/cert chain file path property method"
        
        if isinstance(filePath, basestring):
            filePath = os.path.expandvars(filePath)
            
        elif filePath is not None:
            raise TypeError("X.509 cert. file path must be a valid string")
        
        self._ssl_cert_filepath = filePath
        
    @property
    def sslCACertFilePath(self):
        """Get file path for list of CA cert or certs used to validate SSL 
        connections
        
        :rtype sslCACertFilePath: basestring
        :return sslCACertFilePathList: file path to file containing concatenated
        PEM encoded CA certificates."""
        return self._ssl_cacert_filepath
    
    @sslCACertFilePath.setter
    def sslCACertFilePath(self, value):
        """Set CA cert file path
        
        :type sslCACertFilePath: basestring, list, tuple or None
        :param sslCACertFilePath: file path to CA certificate file.  If None
        then the input is quietly ignored."""
        if isinstance(value, basestring):
            self._ssl_cacert_filepath = os.path.expandvars(value)
            
        elif value is None:
            self._ssl_cacert_filepath = value
            
        else:
            raise TypeError("Input CA Certificate file path must be "
                            "a valid string or None type: %r" % type(value)) 
       
    @property
    def sslCACertDir(self):
        """Get file path for list of CA cert or certs used to validate SSL 
        connections
        
        :rtype sslCACertDir: basestring
        :return sslCACertDirList: directory containing PEM encoded CA 
        certificates."""
        return self._ssl_ca_cert_dir
    
    @sslCACertDir.setter
    def sslCACertDir(self, value):
        """Set CA cert or certs to validate AC signatures, signatures
        of Attribute Authority SOAP responses and SSL connections where 
        AA SOAP service is run over SSL.
        
        :type sslCACertDir: basestring
        :param sslCACertDir: directory containing CA certificate files.
        """
        if isinstance(value, basestring):
            self._ssl_ca_cert_dir = os.path.expandvars(value)
        elif value is None:
            self._ssl_ca_cert_dir = value
        else:
            raise TypeError("Input CA Certificate directroy must be "
                            "a valid string or None type: %r" % type(value))      
      
    @property
    def ssl_valid_hostname(self):
        return self._ssl_valid_hostname
    
    @ssl_valid_hostname.setter
    def ssl_valid_hostname(self, value):
        if isinstance(value, basestring):  
            self._ssl_valid_hostname = value          
        else:
            raise TypeError('Expecting list/tuple or basestring type for "%s" '
                        'attribute; got %r' %
                        (SSLContextProxyInterface.SSL_VALID_HOSTNAME_OPTNAME, 
                         type(value)))
        
    @property
    def ssl_valid_x509_subj_names(self):
        return self._ssl_valid_x509_subj_names

    @ssl_valid_x509_subj_names.setter
    def ssl_valid_x509_subj_names(self, value):
        if isinstance(value, basestring):  
            pat = SSLContextProxyInterface.VALID_DNS_PAT
            self._ssl_valid_x509_subj_names = pat.split(value)
            
        else:
            raise TypeError('Expecting list/tuple or basestring type for "%s" '
                    'attribute; got %r' %
                    (SSLContextProxyInterface.SSL_VALID_X509_SUBJ_NAMES_OPTNAME, 
                     type(value)))

    @property
    def sslPriKeyFilePath(self):
        return self._ssl_prikey_filepath
    
    @sslPriKeyFilePath.setter
    def sslPriKeyFilePath(self, filePath):
        "Set ssl private key file path property method"
        
        if isinstance(filePath, basestring):
            filePath = os.path.expandvars(filePath)

        elif filePath is not None:
            raise TypeError("Private key file path must be a valid "
                            "string or None type")
        
        self._ssl_prikey_filepath = filePath

    @property
    def sslPriKeyPwd(self):
        "Get property method for SSL private key"
        return self._ssl_prikey_pwd
    
    @sslPriKeyPwd.setter
    def sslPriKeyPwd(self, sslPriKeyPwd):
        "Set method for ssl private key file password"
        if not isinstance(sslPriKeyPwd, (type(None), basestring)):
            raise TypeError("Signing private key password must be None "
                            "or a valid string")
        
        self._ssl_prikey_pwd = sslPriKeyPwd

    def __getstate__(self):
        '''Enable pickling for use with beaker.session'''
        _dict = {}
        for attrName in SSLContextProxyInterface.__slots__:
            # Ugly hack to allow for derived classes setting private member
            # variables
            if attrName.startswith('__'):
                attrName = "_SSLContextProxyInterface" + attrName
                
            _dict[attrName] = getattr(self, attrName)
            
        return _dict
        
    def __setstate__(self, attrDict):
        '''Enable pickling for use with beaker.session'''
        for attr, val in attrDict.items():
            setattr(self, attr, val)
