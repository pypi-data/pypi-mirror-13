from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from djutil.models import TimeStampedModel
from django.conf import settings

import json


# New custom data-type django, use this if you want to store a dict !
class DictField(models.TextField):
    """
    JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly.
    Django snippet #1478

    example:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)


        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()
    """

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            # Handle appropriately
            pass
        return value

    def get_db_prep_save(self, value, *args, **kwargs):
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(DictField, self).get_db_prep_save(value, *args, **kwargs)


class Tracker(TimeStampedModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tracked_user", null=True, blank=True)
    path = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    data = DictField(null=True, blank=True)

    class Meta:
        app_label = 'core'

