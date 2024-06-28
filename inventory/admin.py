# Register your models here.
from django.contrib import admin
from rangefilter.filter import DateRangeFilter
from import_export.admin import ExportActionModelAdmin
from .models import *


# Register your models here.
class EmployeeAdmin(ExportActionModelAdmin):
    list_display = (
    	"employee",
        "name",
        "email",
        "apikey"
    )
    search_fields = [
    	"employee",
        "name",
        "email",
        "apikey"
    ]

admin.site.register(Employee, EmployeeAdmin)
