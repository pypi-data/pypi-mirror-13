from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

@python_2_unicode_compatible
class Link(models.Model):
    uri = models.URLField(unique=True)   
    last_checked = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nano_link_link'

    def __str__(self):
        return self.uri

    def verify(self):
        pass
