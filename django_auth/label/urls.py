#
from django.conf.urls import url   # A function that takes a prefix, and an arbitrary number of URL patterns,
# and returns a list of URL patterns in the format Django needs.
from django.urls import path


from . import views

urlpatterns = [
    path('api/label/create/', views.create.as_view(), name='create'),  # Createlabel
    path('api/label/delete/', views.delete.as_view(), name='delete'),  # Deletelabel
    path('api/label/update/', views.update.as_view(), name='update'),  # Updatelabel
    path('api/label/add/', views.add.as_view(), name='add'),
    path('api/label/remove/', views.deletelabel.as_view(), name='remove'),
    path('api/label/get/', views.getLabelOnNotes.as_view(), name='get'),
]