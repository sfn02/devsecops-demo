from django.contrib import admin
from users.models import User,Patient,Doctor

# Register your models here.
admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Patient)