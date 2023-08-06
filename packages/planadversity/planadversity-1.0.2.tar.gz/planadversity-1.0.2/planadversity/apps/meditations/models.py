from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import ShortUUIDField
from django.contrib.auth import get_user_model


class Meditation(TimeStampedModel):
    text = models.TextField(_('Meditation Text'))
    slug = models.IntegerField(_('Day of the Year'))
    date = models.DateField(_('Date'), blank=True, null=True)


    def __unicode__(self):
        return u'{0}'.format(self.slug)

    @permalink
    def get_absolute_url(self):
        return ('meditation-detail', None, {'slug': self.slug})

    def save(self, *args, **kwargs):
        start_date = datetime.strptime(getattr(settings, 'MEDITATION_START_DATE', '2015-01-01'), '%Y-%m-%d')
        self.date = start_date + timedelta(days=(self.slug-1))
        super(Meditation, self).save(*args, **kwargs)


class Response(TimeStampedModel):
    slug = ShortUUIDField(_('slug'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    meditation = models.ForeignKey(Meditation)
    initial_response = models.CharField(_('Initial Response'), max_length=255,
                                        blank=True, null=True)
    desired_response = models.CharField(_('Desired Response'), max_length=255,
                                        blank=True, null=True)
    notes = models.TextField(_('Notes'))



    class Meta:
        ordering = ('-created',)


    def __unicode__(self):
        return u'{0} response by {1}'.format(self.meditation, self.user)

    @permalink
    def get_absolute_url(self):
        return ('response-detail', None, {'slug': self.slug})
