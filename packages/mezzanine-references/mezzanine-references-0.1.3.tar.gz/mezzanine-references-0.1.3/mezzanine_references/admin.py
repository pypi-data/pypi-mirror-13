from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from .models import References, Reference


class ReferenceInline(TabularDynamicInlineAdmin):
    model = Reference


class ReferencesAdmin(PageAdmin):
    inlines = (ReferenceInline,)

admin.site.register(References, ReferencesAdmin)
