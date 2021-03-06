# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
django-pstore -- Python Protected Password Store (Django app)
Copyright (C) 2012,2013  Walter Doekes <wdoekes>, OSSO B.V.

    This application is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation; either version 3 of the License, or (at
    your option) any later version.

    This application is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this application; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,
    USA.
"""
from base64 import b64decode, b64encode

from django.db import models


class Model(models.Model):
    """
    Abstract Django Model that adds default created/modified fields and
    a clone method.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Django metaclass information."""
        abstract = True


class AsciiField(models.CharField):
    """
    MySQL ASCII field.

    Please run the Django unit tests to see if it works as advertised.
    """
    description = 'ASCII'

    def get_prep_value(self, value):
        return value.encode('ascii', 'replace')

    def db_type(self, **kwargs):
        return 'VARBINARY(%s)' % (self.max_length,)


class BlobField(models.Field):
    """
    MySQL BLOB field.

    Please run the Django unit tests to see if it works as advertised.
    """
    description = 'Binary'

    #
    # The to_python and value_to_string methods here are used for serializing
    # to fixtures. Internally, the data is passed as bytestrings.
    #

    def to_python(self, value):
        """
        Differentiates between unicode and binary strings! unicode values are
        expected to be serialized input from fixtures (and thus base64
        encoded). Binary string values are left as-is.
        """
        if isinstance(value, unicode):
            return b64decode(value)
        return value

    def value_to_string(self, obj):
        """
        Return unicode to flag that we're dealing with serialized data. This
        can be used in fixtures.
        """
        value = self._get_val_from_obj(obj)
        return unicode(b64encode(value))

    def db_type(self, **kwargs):
        # We use a LONGBLOB which can hold up to 4GB of bytes. A MEDIUMBLOB of
        # max 16MB should probably be enough, but we don't want to add an
        # arbitrary limit there.
        return 'LONGBLOB'
