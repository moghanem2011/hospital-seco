# in admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HospitalUser

class HospitalUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'gender', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'gender')
    list_filter = ("gender", "is_staff", "is_superuser", "is_active", "groups")
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'gender'),
        }),
    )

    show_facets = admin.ShowFacets.ALLOW


admin.site.register(HospitalUser, HospitalUserAdmin)
