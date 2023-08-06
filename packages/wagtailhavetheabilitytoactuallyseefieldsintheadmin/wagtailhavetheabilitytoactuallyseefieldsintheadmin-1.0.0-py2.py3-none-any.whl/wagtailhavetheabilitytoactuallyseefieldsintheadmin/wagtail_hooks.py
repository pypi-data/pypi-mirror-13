from django.utils.html import format_html
from django.conf import settings

from wagtail.wagtailcore import hooks


@hooks.register('insert_editor_css')
def have_the_ability_to_actually_see_fields_in_the_admin():
    return format_html(
        '<link rel="stylesheet" href="' + settings.STATIC_URL + 'wagtailhavetheabilitytoactuallyseefieldsintheadmin/css/wagtailhavetheabilitytoactuallyseefieldsintheadmin.css">'
    )
