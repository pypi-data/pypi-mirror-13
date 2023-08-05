"""
    CAS authentication backend
"""

import logging
import urllib2
from urllib import urlencode, urlopen
from urlparse import urljoin

from django.conf import settings
from django.contrib.auth.models import User

__all__ = [
    'CASBackend'
]
logger = logging.getLogger(
    __name__
)


def _verify_simple(
    ticket,
    service
):
    """
        Verifies CAS 1.0 authentication ticket.
        Returns username on success and None on failure.
    """

    params = {
        'ticket': ticket,
        'service': service
    }
    url = urljoin(
        settings.CAS_SERVER_URL,
        'serviceValidate'
    ) + '?' + urlencode(
        params
    )
    page = urlopen(
        url
    )
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip(), None
        else:
            return None, None
    finally:
        page.close()
    return None, None


def _verify_with_attributes(ticket, service):
    """
        Verifies CAS XML-based authentication ticket and returns extended
        attributes. Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {
        'ticket': ticket,
        'service': service
    }
    url = urljoin(
        settings.CAS_SERVER_URL,
        'serviceValidate'
    ) + '?' + urlencode(
        params
    )
    page = urlopen(
        url
    )    
    response = page.read()
    logger.debug(
        'Got response from CAS:\n' + str(
            response
        )
    )
    try:
        user = None
        attributes = {}
        tree = ElementTree.fromstring(
            response
        )
        if tree[0].tag.endswith('authenticationSuccess'):
            for element in tree[0]:
                if element.tag.endswith('user'):
                    user = element.text
                elif element.tag.endswith('attributes'):
                    for attribute in element:
                        attributes[
                            attribute.tag.split("}").pop()
                        ] = attribute.text
        return user, attributes
    except Exception as e:
        logger.error(
            e
        )
    finally:
        page.close()


def get_saml_assertion(ticket):
    return """
<?xml version="1.0" encoding="UTF-8"?>
  <SOAP-ENV:Envelope
      xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body>
      <samlp:Request
          xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
          MajorVersion="1"
          MinorVersion="1"
          RequestID="_192.168.16.51.1024506224022"
          IssueInstant="2002-06-19T17:03:44.022Z">
        <samlp:AssertionArtifact>
            """ + ticket + """
        </samlp:AssertionArtifact>
      </samlp:Request>
    </SOAP-ENV:Body>
  </SOAP-ENV:Envelope>
"""

SAML_1_0_NS = 'urn:oasis:names:tc:SAML:1.0:'
SAML_1_0_PROTOCOL_NS = '{' + SAML_1_0_NS + 'protocol' + '}'
SAML_1_0_ASSERTION_NS = '{' + SAML_1_0_NS + 'assertion' + '}'


def _verify_cas2_saml(ticket, service):
    """
        Verifies CAS 3.0+ XML-based authentication ticket and returns extended
        attributes.
        Returns username and attributes on success and None, None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    # We do the SAML validation
    headers = {
        'soapaction': 'http://www.oasis-open.org/committees/security',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'accept': 'text/xml',
        'connection': 'keep-alive',
        'content-type': 'text/xml'
    }
    params = {
        'TARGET': service
    }
    url = urllib2.Request(
        urljoin(
            settings.CAS_SERVER_URL,
            'samlValidate'
        ) + '?' + urlencode(
            params
        ),
        '',
        headers
    )
    url.add_data(
        get_saml_assertion(
            ticket
        )
    )
    page = urllib2.urlopen(
        url
    )
    try:
        user = None
        attributes = {}
        response = page.read()
        logger.debug(
            'Got response from CAS:\n' + str(
                response
            )
        )
        tree = ElementTree.fromstring(
            response
        )
        # Find the authentication status
        success = tree.find(
            './/' + SAML_1_0_PROTOCOL_NS + 'StatusCode'
        )
        if success is not None and success.attrib['Value'] == 'samlp:Success':
            # User is validated
            attrs = tree.findall(
                './/' + SAML_1_0_ASSERTION_NS + 'Attribute'
            )
            for at in attrs:
                if 'uid' in at.attrib.values():
                    user = at.find(
                        SAML_1_0_ASSERTION_NS + 'AttributeValue'
                    ).text
                    attributes['uid'] = user
                values = at.findall(
                    SAML_1_0_ASSERTION_NS + 'AttributeValue'
                )
                if len(values) > 1:
                    values_array = []
                    for v in values:
                        values_array.append(
                            v.text
                        )
                    attributes[at.attrib['AttributeName']] = values_array
                else:
                    attributes[at.attrib['AttributeName']] = values[0].text
        return user, attributes
    except Exception as e:
        logger.error(e)
    finally:
        page.close()


_PROTOCOLS = {
    '1': _verify_simple,
    '2': _verify_with_attributes,
    '3': _verify_with_attributes,
    'CAS_2_SAML_1_0': _verify_cas2_saml
}


if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


class CASBackend(
    object
):
    """
        CAS authentication backend
    """

    def __init__(self):
        super(CASBackend, self).__init__()

    def authenticate(self, ticket, service, request):
        """
            Verifies CAS ticket and gets or creates User object
        """

        logger.debug(
            'Attempting to validate ' + str(
                ticket
            )
        )
        username, attributes = _verify(
            ticket,
            service
        )
        logger.debug(
            'Authenticated ' + str(
                username
            )
        )
        if attributes:
            request.session['attr'] = attributes
        if not username:
            return None
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
        user.save()
        return user

    def get_user(
        self,
        user_id
    ):
        """
            Retrieve the user's entry in the User model if it exists
        """

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
