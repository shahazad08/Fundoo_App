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
from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

# schema_view = get_swagger_view(title='APIView')

schema_view = get_schema_view(
    title='A Different API',
    renderer_classes=[CoreJSONRenderer]
)
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

    # path('upload_profileimage/', views.upload_profileimage, name='upload_profileimage'),

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('api/createnotes/', views.createnotes.as_view(), name='createnotes'),  # For Create
    path('api/deletenote/', views.deletenote.as_view(), name='deletenote'),  # Delete with PK
    path('api/delete_from_trash/', views.delete_from_trash.as_view(), name='delete_from_trash'),  # Delete with PK
    path('api/updatenote/', views.updatenote.as_view(), name='updatenote'),  # Update with Pk
    path('api/archivenote/', views.archivenote.as_view(), name='archivenote'),  # Update with Pk
    path('api/notarchivenote/', views.notarchivenote.as_view(), name='notarchivenote'),  # Update with Pk

    path('api/restorenote/', views.restorenote.as_view(), name='restorenote'),  # Update with Pk
    path('api/colornote/', views.colornote.as_view(), name='colornote'),  # Update with Pk
    path('api/ispinned/', views.ispinned.as_view(), name='ispinned'),  # Update with Pk
    path('api/unpinned/', views.unpinned.as_view(), name='unpinned'),  # Update with Pk
    path('api/showpinned/', views.showpinned, name='showpinned'),  # Update with Pk
    path('api/copynote/', views.copynote.as_view(), name='copynote'),  # Update with Pk
    path('api/table/', views.table, name='table'),  # Displays the Table data in a front view using jinga template
    path('api/showarchive/', views.showarchive, name='showarchive'),

    path('api/trash/', views.trash, name='trash'),  # Displays the Table data in a front view using jinga template
    path('api/page/', views.PostListAPIView.as_view(), name='page'),  # Paginate
    path('api/create_label/', views.create_label.as_view(), name='create_label'),  # Createlabel
    path('api/deletelabel/', views.deletelabel.as_view(), name='deletelabel'),  # Deletelabel
    path('api/updatelabel/', views.updatelabel.as_view(), name='updatelabel'),  # Updatelabel
    path('api/addLabelOnNote/<int:pk>/', views.addLabelOnNote.as_view(), name='addLabelOnNote'),
    path('api/getLabelOnNotes/', views.getLabelOnNotes.as_view(), name='getLabelOnNotes'),
    path('api/removeLabelonNote/<int:pk>/', views.removeLabelonNote.as_view(), name='removeLabelonNote'),
    # Displays the Labels data in a front view using jinga template
    # url(r'^docs/', schema_view),

    path('api/getnote/', views.getnote.as_view(), name='getnote'),
    path('api/showlabels/', views.showlabels, name='showlabels'),
    # path('createcollaborator/<int:pk>/', views.createcollaborator, name='createcollaborator'),
    path('api/createcollaborator/', views.createcollaborator.as_view(), name='createcollaborator'),
    path('api/deletecollaborator/', views.deletecollaborator.as_view(), name='deletecollaborator'),
    path('api/remainder/', views.remainder.as_view(), name='remainder'),
    #get_all_notes
    path('api/login/', views.Login.as_view(), name='login'),
    # path('api/dummy_site/', views.dummy_site.as_view(), name='dummy_site'),



]
