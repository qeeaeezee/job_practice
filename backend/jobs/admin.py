from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'posting_date', 'expiration_date', 'status', 'is_active', 'is_scheduled')
    list_filter = ('is_active', 'is_scheduled', 'location', 'company_name')
    search_fields = ('title', 'description', 'company_name', 'location')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'company_name', 'location', 'salary_range')
        }),
        ('Dates & Status', {
            'fields': ('posting_date', 'expiration_date', 'is_active', 'is_scheduled')
        }),
        ('Skills', {
            'fields': ('required_skills',)
        }),
    )
