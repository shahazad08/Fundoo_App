from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url, include
from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
# from rest_framework.decorators import api_view
# admin.autodiscover()
from users import views
from django.contrib import auth

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
    path('admin/', admin.site.urls),  # for a admin login
    path('', include('users.urls'))
]
