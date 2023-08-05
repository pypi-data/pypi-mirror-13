from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from .models import FaqPage, FaqQuestion


class FaqQuestionInline(TabularDynamicInlineAdmin):
    model = FaqQuestion


class FaqPageAdmin(PageAdmin):
    inlines = (FaqQuestionInline,)

admin.site.register(FaqPage, FaqPageAdmin)
