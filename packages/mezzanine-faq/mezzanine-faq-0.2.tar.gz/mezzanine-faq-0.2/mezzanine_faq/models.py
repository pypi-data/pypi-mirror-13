# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page


class FaqPage(Page):
    pass

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQ")


class FaqQuestion(Orderable):
    page = models.ForeignKey(FaqPage)
    question = models.TextField(_("Question"))
    answer = models.TextField(_("Answer"))

    class Meta:
        order_with_respect_to = "page"
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
