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

from datetime import datetime

from django.core.management.base import BaseCommand

from django_ca.models import Certificate


class Command(BaseCommand):
    help = "List all certificates."

    def add_arguments(self, parser):
        parser.add_argument('--expired', default=False, action='store_true',
                            help='Also list expired certificates.')
        parser.add_argument('--revoked', default=False, action='store_true',
                            help='Also list revoked certificates.')

    def handle(self, *args, **options):
        certs = Certificate.objects.all()

        if not options['expired']:
            certs = certs.filter(expires__gt=datetime.now())
        if not options['revoked']:
            certs = certs.filter(revoked=False)

        for cert in certs:
            if cert.revoked is True:
                info = 'revoked'
            else:
                info = 'expires: %s' % cert.expires.strftime('%Y-%m-%d')
            self.stdout.write('%s: %s (%s)' % (cert.serial, cert.cn, info))
