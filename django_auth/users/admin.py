from django.contrib import admin
from .models import User,CreateNotes
# from adminplus.sites import AdminSitePlus

admin.site.register(User)
# admin.site.register(Notes)
# admin.site.register(Notes)
# admin.site.register(Notes)
# admin.site.register(RestRegistration)
admin.site.register(CreateNotes)
admin.autodiscover()