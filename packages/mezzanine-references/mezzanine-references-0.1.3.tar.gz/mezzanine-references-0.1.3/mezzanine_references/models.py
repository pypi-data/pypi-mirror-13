# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page


class References(Page):
    image_style = models.CharField(_("Image style"), choices=(
        ('rounded', _('Rounded')),
        ('circle', _('Circle')),
        ('thumbnail', _('Thumbnail')),
        ('default', _('Default')),
    ), default='default', max_length=12)
    image_size = models.PositiveIntegerField(_("Image width in pixels"), default=200)

    link_style = models.CharField(_("Link style"), choices=(
        ('button', _('Button')),
        ('text', _('Text')),
    ), default='button', max_length=12)
    button_style = models.CharField(_("Button style"), choices=(
        ('default', 'default'),
        ('primary', 'primary'),
        ('info', 'info'),
        ('warning', 'warning'),
        ('danger', 'danger'),
    ), default='default', max_length=12)


class Reference(Orderable):
    page = models.ForeignKey(References)
    content = models.TextField(_("Content"))
    name = models.CharField(_("Name"), max_length=32)
    subtitle = models.CharField(_("Subtitle"), max_length=32, null=True, blank=True)
    date = models.DateField(_("Date of realization"), null=True, blank=True)
    image = models.ImageField(upload_to="references", null=True, blank=True)

    link = models.CharField(_("Link"), max_length=128, null=True, blank=True)
    link_title = models.CharField(_("Link title"), max_length=32, null=True, blank=True)
    link_new_window = models.BooleanField(_("Open link on new page"), default=False)

    class Meta:
        order_with_respect_to = "page"
