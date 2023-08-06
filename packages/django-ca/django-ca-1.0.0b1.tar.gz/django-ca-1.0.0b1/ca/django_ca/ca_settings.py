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

import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

CA_DIR = getattr(settings, 'CA_DIR', os.path.join(settings.BASE_DIR, 'files'))

# exact certificate locations are not documented, but you may still override them if you know what
# you're doing.
CA_KEY = getattr(settings, 'CA_KEY', os.path.join(CA_DIR, 'ca.key'))
CA_CRT = getattr(settings, 'CA_CRT', os.path.join(CA_DIR, 'ca.crt'))

CA_PROFILES = {
    'client': {
        # see: http://security.stackexchange.com/questions/68491/
        'desc': _('A certificate for a client.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:FALSE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'digitalSignature',
            ],
        },
        'extendedKeyUsage': {
            'critical': False,
            'value': [
                'clientAuth',
            ],
        },
    },
    'server': {
        'desc': _('A certificate for a server, allows client and server authentication.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:FALSE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'digitalSignature',
                'keyAgreement',
                'keyEncipherment',
            ],
        },
        'extendedKeyUsage': {
            'critical': False,
            'value': [
                'clientAuth',
                'serverAuth',
            ],
        },
    },
    'webserver': {
        # see http://security.stackexchange.com/questions/24106/
        'desc': _('A certificate for a webserver.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:FALSE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'digitalSignature',
                'keyAgreement',
                'keyEncipherment',
            ],
        },
        'extendedKeyUsage': {
            'critical': False,
            'value': [
                'serverAuth',
            ],
        },
    },
    'enduser': {
        # see: http://security.stackexchange.com/questions/30066/
        'desc': _(
            'A certificate for an enduser, allows client authentication, code and email signing.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:FALSE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'dataEncipherment',
                'digitalSignature',
                'keyEncipherment',
            ],
        },
        'extendedKeyUsage': {
            'critical': False,
            'value': [
                'clientAuth',
                'codeSigning',
                'emailProtection',
            ],
        },
        'cn_in_san': False,
    },
    'ocsp': {
        'desc': _('A certificate for an OCSP responder.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:FALSE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'nonRepudiation',
                'digitalSignature',
                'keyEncipherment',
            ],
        },
        'extendedKeyUsage': {
            'critical': False,
            'value': [
                'OCSPSigning',
            ],
        },
    },
    'ca': {
        'desc': _('A CA certificate.'),
        'basicConstraints': {
            'critical': True,
            'value': 'CA:TRUE',
        },
        'keyUsage': {
            'critical': True,
            'value': [
                'cRLSign',
                'keyCertSign',
            ],
        },
        'extendedKeyUsage': None,
    },
}

_CA_DEFAULT_SUBJECT = getattr(settings, 'CA_DEFAULT_SUBJECT', {})
for name, profile in CA_PROFILES.items():
    profile['subject'] = _CA_DEFAULT_SUBJECT
    profile.setdefault('cn_in_san', True)

# Add ability just override/add some profiles
_CA_PROFILE_OVERRIDES = getattr(settings, 'CA_PROFILES', {})
for name, profile in _CA_PROFILE_OVERRIDES.items():
    if settings is None:
        del CA_PROFILES[name]
    elif name in CA_PROFILES:
        CA_PROFILES[name].update(profile)
    else:
        profile.setdefault('subject', _CA_DEFAULT_SUBJECT)
        profile.setdefault('cn_in_san', True)
        CA_PROFILES[name] = profile

CA_ALLOW_CA_CERTIFICATES = getattr(settings, 'CA_ALLOW_CA_CERTIFICATES', False)
CA_DEFAULT_EXPIRES = getattr(settings, 'CA_DEFAULT_EXPIRES', 730)
CA_DEFAULT_PROFILE = getattr(settings, 'CA_DEFAULT_PROFILE', 'webserver')
CA_DIGEST_ALGORITHM = getattr(settings, 'CA_DIGEST_ALGORITHM', "sha512")
CA_OCSP = getattr(settings, 'CA_OCSP', None)
CA_OCSP_INDEX_PATH = getattr(settings, 'CA_OCSP_INDEX_PATH', None)
CA_ISSUER = getattr(settings, 'CA_ISSUER', None)
CA_ISSUER_ALT_NAME = getattr(settings, 'CA_ISSUER_ALT_NAME', None)
CA_CRL_DISTRIBUTION_POINTS = getattr(settings, 'CA_CRL_DISTRIBUTION_POINTS', None)
CA_CRL_SETTINGS = getattr(settings, 'CA_CRL_SETTINGS', None)
