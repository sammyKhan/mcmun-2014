from django.contrib import admin

from mcmun.models import RegisteredSchool, ScholarshipApp, SecretariatMember, \
    Coordinator, ScheduleItem


class RegisteredSchoolAdmin(admin.ModelAdmin):
    # Sort reverse chronologically
    ordering = ['-id']
    list_display = ('school_name', 'id', 'email', 'is_approved',
                    'num_delegates', 'amount_owed', 'amount_paid')
    list_filter = ('is_approved', 'use_online_payment')
    exclude = ('account',)
    search_fields = ('school_name', 'email')

class ScheduleItemAdmin(admin.ModelAdmin):
    ordering = ['start_time']
    list_display = ('name', 'start_time', 'end_time', 'is_visible')


admin.site.register(RegisteredSchool, RegisteredSchoolAdmin)
admin.site.register(ScholarshipApp)
admin.site.register(SecretariatMember)
admin.site.register(Coordinator)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
