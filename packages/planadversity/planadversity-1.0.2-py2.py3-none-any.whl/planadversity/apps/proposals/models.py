from django.db import models
from localflavor.us.models import PhoneNumberField, USStateField
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django_extensions.db.models import (TitleSlugDescriptionModel,
                                         TimeStampedModel)
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class Meditation(TimeStampedModel):
    text = models.TextField(_('Meditation Text'))
    slug = models.IntegerField(_('Day of the Year'))
    date = models.DateField(_('Date'), blank=True, null=True)
    slug = models.SlugField(_('slug'))


    def __unicode__(self):
        return u'{0} - {1}'.format(self.day, self.title)

    @permalink
    def get_absolute_url(self):
        return ('meditation-detail', None, {'slug': self.slug})


class Response(TimeStampedModel):
    pass
