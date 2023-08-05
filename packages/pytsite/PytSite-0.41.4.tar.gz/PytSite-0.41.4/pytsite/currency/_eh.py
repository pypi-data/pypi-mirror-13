"""Event Handlers
"""
from pytsite import form as _form, auth as _auth
from . import _widget

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def auth_profile_form_render(frm: _form.Form):
    user = _get_profile_form_user(frm)


def _get_profile_form_user(frm: _form.Form) -> _auth.model.User:
    print(frm.get_widget('__'))
