# -*- coding: utf-8 -*-
#
# This file is part of django-ca (https://github.com/mathiasertl/django-ca).
#
# django-ca is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# django-ca is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-ca.  If not,
# see <http://www.gnu.org/licenses/>.

"""Central functions to load CA key and cert as PKey/X509 objects."""

import re
import uuid

from datetime import datetime
from datetime import timedelta
from ipaddress import ip_address

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _

from OpenSSL import crypto

from django_ca import ca_settings

_CA_KEY = None
_CA_CRT = None

# Description strings for various X509 extensions, taken from "man x509v3_config".
EXTENDED_KEY_USAGE_DESC = _('Purposes for which the certificate public key can be used for.')
KEY_USAGE_DESC = _('Permitted key usages.')
SAN_OPTIONS_RE = '(email|URI|IP|DNS|RID|dirName|otherName):'


class LazyEncoder(DjangoJSONEncoder):
    """Encoder that also encodes translated strings."""

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


def format_date(date):
    """Format date as ASN1 GENERALIZEDTIME, as required by various fields."""
    return date.strftime('%Y%m%d%H%M%SZ')


def get_ca_key(reload=False):
    global _CA_KEY
    if _CA_KEY is None or reload is True:
        with open(ca_settings.CA_KEY) as ca_key:
            _CA_KEY = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key.read())
    return _CA_KEY


def get_ca_crt(reload=False):
    global _CA_CRT
    if _CA_CRT is None or reload is True:
        with open(ca_settings.CA_CRT) as ca_crt:
            _CA_CRT = crypto.load_certificate(crypto.FILETYPE_PEM, ca_crt.read())
    return _CA_CRT


def get_basic_cert(expires):
    not_before = format_date(datetime.utcnow() - timedelta(minutes=5))
    not_after = format_date(expires)

    cert = crypto.X509()
    cert.set_serial_number(uuid.uuid4().int)
    cert.set_notBefore(not_before.encode('utf-8'))
    cert.set_notAfter(not_after.encode('utf-8'))
    return cert


def get_cert_profile_kwargs(name=None):
    """Get kwargs suitable for get_cert X509 keyword arguments from the given profile."""

    if name is None:
        name = ca_settings.CA_DEFAULT_PROFILE

    profile = ca_settings.CA_PROFILES[name]
    kwargs = {
        'cn_in_san': profile['cn_in_san'],
        'subject': profile['subject'],
    }
    for arg in ['basicConstraints', 'keyUsage', 'extendedKeyUsage']:
        config = profile[arg]
        if config is None:
            continue

        critical = config.get('critical', 'True')
        if isinstance(config['value'], str):
            kwargs[arg] = (critical, bytes(config['value'], 'utf-8'))
        elif isinstance(config['value'], bytes):
            kwargs[arg] = (critical, config['value'])
        else:
            kwargs[arg] = (critical, bytes(','.join(config['value']), 'utf-8'))
    return kwargs


def get_cert(csr, expires, subject=None, cn_in_san=True, csr_format=crypto.FILETYPE_PEM, algorithm=None,
             basicConstraints='critical,CA:FALSE', subjectAltName=None, keyUsage=None,
             extendedKeyUsage=None):
    """Create a signed certificate from a CSR.

    X509 extensions (`basic_constraints`, `key_usage`, `ext_key_usage`) may either be None (in
    which case they are not added) or a tuple with the first value being a bool indicating if the
    value is critical and the second value being a byte-array indicating the extension value.
    Example::

        (True, b'CA:FALSE')

    Parameters
    ----------

    csr : str
        A valid CSR in PEM format. If none is given, `self.csr` will be used.
    expires : datetime
        When the certificate should expire.
    subject : dict, optional
        The Subject to use in the certificate.  The keys of this dict are the fields of an X509
        subject, that is `"C"`, `"ST"`, `"L"`, `"OU"` and `"CN"`. If ommited or if the value does
        not contain a `"CN"` key, the first value of the `subjectAltName` parameter is used as
        CommonName (and is obviously mandatory in this case).
    cn_in_san : bool, optional
        Wether the CommonName should also be included as subjectAlternativeName. The default is
        `True`, but the parameter is ignored if no CommonName is given. This is typically set to
        `False` when creating a client certificate, where the subjects CommonName has no meaningful
        value as subjectAltName.
    csr_format : int, optional
        The format of the submitted CSR request. One of the OpenSSL.crypto.FILETYPE_*
        constants. The default is PEM.
    algorithm : {'sha512', 'sha256', ...}, optional
        Algorithm used to sign the certificate. The default is the CA_DIGEST_ALGORITHM setting.
    subjectAltName : list of str, optional
        A list of values for the subjectAltName extension. Values are passed to
        `get_subjectAltName`, see function documentation for how this value is parsed.
    basicConstraints : tuple or None
        Value for the `basicConstraints` X509 extension. See description for format details.
    keyUsage : tuple or None
        Value for the `keyUsage` X509 extension. See description for format details.
    extendedKeyUsage : tuple or None
        Value for the `extendedKeyUsage` X509 extension. See description for format details.

    Returns
    -------

    OpenSSL.crypto.X509
        The signed certificate.
    """
    if subject is None:
        subject = {}
    if not subject.get('CN') and not subjectAltName:
        raise ValueError("Must at least cn or subjectAltName parameter.")

    req = crypto.load_certificate_request(csr_format, csr)

    # get algorithm used to sign certificate
    if not algorithm:
        algorithm = ca_settings.CA_DIGEST_ALGORITHM

    # get CA key and cert
    ca_crt = get_ca_crt()
    ca_key = get_ca_key()

    # Process CommonName and subjectAltName extension.
    if subject.get('CN') is None:
        subject['CN'] = re.sub('^%s' % SAN_OPTIONS_RE, '', subjectAltName[0])
        subjectAltName = get_subjectAltName(subjectAltName)
    elif cn_in_san is True:
        if subjectAltName:
            subjectAltName = get_subjectAltName(subjectAltName, cn=subject['CN'])
        else:
            subjectAltName = get_subjectAltName([subject['CN']])

    # subjectAltName might still be None, in which case the extension is not added.
    elif subjectAltName:
        subjectAltName = get_subjectAltName(subjectAltName)

    # Create signed certificate
    cert = get_basic_cert(expires)
    cert.set_issuer(ca_crt.get_subject())
    for key, value in subject.items():
        setattr(cert.get_subject(), key, bytes(value, 'utf-8'))
    cert.set_pubkey(req.get_pubkey())

    extensions = [
        crypto.X509Extension(b'subjectKeyIdentifier', 0, b'hash', subject=cert),
        crypto.X509Extension(b'authorityKeyIdentifier', 0, b'keyid,issuer', issuer=ca_crt),
    ]

    if keyUsage is not None:
        extensions.append(crypto.X509Extension(b'keyUsage', *keyUsage))
    if extendedKeyUsage is not None:
        extensions.append(crypto.X509Extension(b'extendedKeyUsage', *extendedKeyUsage))

    if basicConstraints is not None:
        extensions.append(crypto.X509Extension(b'basicConstraints', *basicConstraints))

    # Add subjectAltNames, always also contains the CommonName
    if subjectAltName is not None:
        extensions.append(crypto.X509Extension(b'subjectAltName', 0, subjectAltName))

    # Set CRL distribution points:
    if ca_settings.CA_CRL_DISTRIBUTION_POINTS:
        value = ','.join(['URI:%s' % uri for uri in ca_settings.CA_CRL_DISTRIBUTION_POINTS])
        value = bytes(value, 'utf-8')
        extensions.append(crypto.X509Extension(b'crlDistributionPoints', 0, value))

    # Add issuerAltName
    if ca_settings.CA_ISSUER_ALT_NAME:
        issuerAltName = bytes('URI:%s' % ca_settings.CA_ISSUER_ALT_NAME, 'utf-8')
    else:
        issuerAltName = b'issuer:copy'
    extensions.append(crypto.X509Extension(b'issuerAltName', 0, issuerAltName, issuer=ca_crt))

    # Add authorityInfoAccess
    auth_info_access = []
    if ca_settings.CA_OCSP:
        auth_info_access.append('OCSP;URI:%s' % ca_settings.CA_OCSP)
    if ca_settings.CA_ISSUER:
        auth_info_access.append('caIssuers;URI:%s' % ca_settings.CA_ISSUER)
    if auth_info_access:
        auth_info_access = bytes(','.join(auth_info_access), 'utf-8')
        extensions.append(crypto.X509Extension(b'authorityInfoAccess', 0, auth_info_access))

    # Add collected extensions
    cert.add_extensions(extensions)

    # Finally sign the certificate:
    cert.sign(ca_key, algorithm)

    return cert


def get_subjectAltName(names, cn=None):
    """Compute the value of the subjectAltName extension based on the given list of names.

    The `cn` parameter, if provided, is prepended if not present in the list of names.

    This method supports the `IP`, `email`, `URI` and `DNS` options automatically, if you need a
    different option (or think the automatic parsing is wrong), give the full value verbatim (e.g.
    `otherName:1.2.3.4;UTF8:some other identifier`.
    """
    values = []
    names = sorted(set(names))
    if cn is not None and cn not in names:
        names.insert(0, cn)

    for name in names:
        if not name:
            continue
        if isinstance(name, bytes):
            name = name.decode('utf-8')

        # Match any known literal values
        if re.match(SAN_OPTIONS_RE, name):
            values.append(name)
            continue

        try:
            ip_address(name)
            values.append('IP:%s' % name)
            continue
        except ValueError:
            pass

        if re.match('[a-z0-9]{2,}://', name):
            values.append('URI:%s' % name)
        elif '@' in name:
            values.append('email:%s' % name)
        else:
            values.append('DNS:%s' % name)

    return bytes(','.join(values), 'utf-8')
