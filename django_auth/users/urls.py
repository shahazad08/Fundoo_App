from django.conf.urls import url   # A function that takes a prefix, and an arbitrary number of URL patterns,
# and returns a list of URL patterns in the format Django needs.
from django.urls import path

from . import views
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework.decorators import api_view
admin.autodiscover()
from users import views
from django.contrib import auth

from .swagger_schema import SwaggerSchemaView

urlpatterns = [
    url(r'^$', views.signup),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^register/$', views.Registerapi.as_view(), name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),

    url(r'^log_me/$', views.log_me, name='log_me'),
    path('log_user/', views.logins, name='log_user'),
    path('logout/', views.exit, name='logout'),
    path('upload_profilenew/', views.upload_profilenew, name='upload_profilenew'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    path('api/table/', views.table, name='table'),  # Displays the Table data in a front view using jinga template
    path('api/showarchive/', views.showarchive, name='showarchive'),
    path('api/trash/', views.trash, name='trash'),  # Displays the Table data in a front view using jinga template
    path('api/showlabels/', views.showlabels, name='showlabels'),
    path('api/login/', views.Login.as_view(), name='login'),
    url(r'^swagger/', SwaggerSchemaView.as_view()),


]
