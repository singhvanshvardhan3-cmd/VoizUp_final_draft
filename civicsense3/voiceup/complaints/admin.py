from django.contrib import admin

# Register your models here.
from .models import Complaint
from . models import StaffNote
# Register your models here.
admin.site.register(Complaint)
admin.site.register(StaffNote)