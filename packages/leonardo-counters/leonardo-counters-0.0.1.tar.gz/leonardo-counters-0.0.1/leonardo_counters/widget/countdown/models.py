# -#- coding: utf-8 -#-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from leonardo.models import Widget


class CountdownWidget(Widget):

    final_time = models.DateTimeField(
        verbose_name=_("Final Time"))

    class Meta:
        abstract = True
        verbose_name = _("Countdown")
        verbose_name_plural = _("Countdowns")
