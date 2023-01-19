from django.urls import path

from images import views

app_name = 'images'

urlpatterns = [
    path('', views.ImageViewSet.as_view({'post': 'create'}), name='create'),
    path('<int:pk>',
         views.ImageViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='retrieve_remove'),
]
