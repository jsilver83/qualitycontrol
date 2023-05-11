from django.contrib import admin
from .models import *


class SectionAdmin(admin.ModelAdmin):
    list_filter = (
        'title_ar',
        'title_en',
        'sub_of',
    )


admin.site.register(Assessment)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Evidence)
