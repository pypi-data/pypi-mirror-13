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

from django.core.management.base import BaseCommand

from django_ca.models import Certificate


class Command(BaseCommand):
    help = "Revoke a certificate."

    def add_arguments(self, parser):
        parser.add_argument('serial', nargs='+',
                            help='Serial of the certificate (see the list_certs command).')
        parser.add_argument('--reason', help="An optional reason for revokation.")

    def handle(self, *args, **options):
        for serial in options.get('serial'):
            try:
                cert = Certificate.objects.get(serial=serial)
                cert.revoke(reason=options.get('reason'))
            except Certificate.DoesNotExist:
                self.stderr.write('Certificate "%s" does not exist.' % serial)
