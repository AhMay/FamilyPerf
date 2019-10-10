from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Family)
admin.site.register(models.MemberInfo)

class PerfItemAdmin(admin.ModelAdmin):
    list_display = ('id','member','name','score_up','score_down')


class PerfRecordAdmin(admin.ModelAdmin):
    list_display = ('day','member','item','score')

admin.site.register(models.PerfItem,PerfItemAdmin)
admin.site.register(models.PerfRecord,PerfRecordAdmin)
admin.site.register(models.Result)
admin.site.register(models.UserProfile)