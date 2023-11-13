from django.urls import path

from images import views

app_name = 'images'

urlpatterns = [
    path('', views.ImageViewSet.as_view({'post': 'create'}), name='image_create'),
    path('<int:pk>',
         views.ImageViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='image_retrieve_remove'),
]
