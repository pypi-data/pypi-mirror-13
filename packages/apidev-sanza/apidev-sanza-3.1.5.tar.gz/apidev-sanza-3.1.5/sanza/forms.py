# -*- coding: utf-8 -*-
"""Sanza : your django CRM"""

from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm

from coop_cms.bs_forms import BootstrapableMixin


class BsAuthenticationForm(BootstrapableMixin, AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(BsAuthenticationForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()


class BsPasswordResetForm(BootstrapableMixin, PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(BsPasswordResetForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()


class BsPasswordChangeForm(BootstrapableMixin, PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(BsPasswordChangeForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()

