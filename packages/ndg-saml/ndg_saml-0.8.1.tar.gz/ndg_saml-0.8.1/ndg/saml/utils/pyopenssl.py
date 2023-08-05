"""SAML 2.0 Utilities module for M2Crypto SSL functionality 

NDG SAML
"""
__author__ = "P J Kershaw"
__date__ = "29/05/15"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import logging
from OpenSSL import SSL, crypto
from OpenSSL.test.test_ssl import verify_cb

from ndg.httpsclient.ssl_peer_verification import ServerSSLCertVerification

from ndg.saml.utils.ssl_context import SSLContextProxyInterface

log = logging.getLogger(__name__)


class SSLContextProxy(SSLContextProxyInterface):
    SSL_PROTOCOL_METHOD = SSL.TLSv1_METHOD
    SSL_VERIFY_DEPTH = 9
    
    __slots__ = ()

    def __call__(self):
        """Create an M2Crypto SSL Context from this objects properties
        :type depth: int
        :param depth: max. depth of certificate to verify against
        :type kw: dict
        :param kw: OpenSSL.SSL.Context keyword arguments
        :rtype: OpenSSL.SSL.Context
        :return: M2Crypto SSL context object
        """
        ctx = SSL.Context(self.__class__.SSL_PROTOCOL_METHOD)
        
        # Configure context according to this proxy's attributes
        if self.sslCertFilePath and self.sslPriKeyFilePath:
            # Pass client certificate (optionally with chain)
            ctx.use_certificate_chain_file(self.sslCertFilePath)
            
            with open(self.sslPriKeyFilePath, 'r') as prikey_file:
                prikey_content = prikey_file.read()
            prikey_file.close()
            
            prikey = crypto.load_privatekey(crypto.FILETYPE_PEM, 
                                            prikey_content, 
                                            self.sslPriKeyPwd)
            
            ctx.use_privatekey(prikey) 

            log.debug("Set client certificate and key in SSL Context")
        else:
            log.debug("No client certificate or key set in SSL Context")
            
        if self.sslCACertFilePath or self.sslCACertDir:
            # Set CA certificates in order to verify peer
            ctx.load_verify_locations(self.sslCACertFilePath, 
                                      self.sslCACertDir)
            mode = SSL.VERIFY_PEER
            ctx.set_verify_depth(self.__class__.SSL_VERIFY_DEPTH)
            
            verify_cb = lambda connection, peerCert, errorStatus, errorDepth, \
                 preverifyOK: preverifyOK
        else:
            mode = SSL.VERIFY_NONE
            log.warning('No CA certificate files set: mode set to '
                        '"verify_none"!  No verification of the server '
                        'certificate will be enforced')
            
        n_ssl_valid_x509_subj_names = len(self.ssl_valid_x509_subj_names)
        if n_ssl_valid_x509_subj_names > 0 or self.ssl_valid_hostname:
            # Set custom callback in order to verify peer certificate DN 
            # against whitelist
            mode = SSL.VERIFY_PEER
            
            if n_ssl_valid_x509_subj_names == 0:
                cert_dn = None
            else:
                cert_dn = self.ssl_valid_x509_subj_names[0]
                
            # Nb. limit - this verification callback can only validate against
            # a single DN not multiples as allowed by the interface class
            ssl_cert_verification = ServerSSLCertVerification(
                                    hostname=self.ssl_valid_hostname,
                                    certDN=cert_dn)
            
            verify_cb = ssl_cert_verification.get_verify_server_cert_func()
            
            log.debug('Set peer certificate Distinguished Name check set in '
                      'SSL Context')
        else:
            log.warning('No peer certificate Distinguished Name check set in '
                        'SSL Context')
            
        ctx.set_verify(mode, verify_cb)
                   
        return ctx
    
    @SSLContextProxyInterface.ssl_valid_x509_subj_names.setter
    def ssl_valid_x509_subj_names(self, value):
        if isinstance(value, basestring):  
            self._ssl_valid_x509_subj_names = [value]        
        else:
            raise TypeError('Expecting a SINGLE string type for "%s" '
                            'attribute; got %r' %
                (SSLContextProxyInterface.SSL_VALID_X509_SUBJ_NAMES_OPTNAME, 
                 type(value)))
