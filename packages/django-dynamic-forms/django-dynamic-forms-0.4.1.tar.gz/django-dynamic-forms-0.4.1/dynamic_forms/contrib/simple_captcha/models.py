# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.decorators import classonlymethod
from django.utils.translation import ugettext_lazy as _

from dynamic_forms.formfields import dynamic_form_field, BaseDynamicFormField


@dynamic_form_field
class CaptchaField(BaseDynamicFormField):

    cls = 'captcha.fields.CaptchaField'
    display_type = _('CAPTCHA')

    class Meta:
        _exclude = ('required',)

    @classonlymethod
    def do_display_data(self):
        return False
