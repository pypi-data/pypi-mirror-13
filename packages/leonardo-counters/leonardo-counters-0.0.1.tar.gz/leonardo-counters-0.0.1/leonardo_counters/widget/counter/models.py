# -#- coding: utf-8 -#-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from leonardo.models import Widget

DIRECTION_CHOICES = (
    ('up', 'Up'),
    ('down', 'Down')
)


class CounterWidget(Widget):

    number = models.BigIntegerField(
        verbose_name=_("Number"))

    direction = models.CharField(
        verbose_name=_("Direction"), default='up', max_length=10,
        choices=DIRECTION_CHOICES)

    interval = models.PositiveIntegerField(
        verbose_name=_("Interval"),
        help_text=_('Defines the time between each counter increment'),
        default=1000)

    format = models.CharField(
        verbose_name=_("Defines the format and the "
                       " limit for each part - default: 23:59:59"),
        default='120',
        max_length=255)

    class Meta:
        abstract = True
        verbose_name = _("Counter")
        verbose_name_plural = _("Counters")
