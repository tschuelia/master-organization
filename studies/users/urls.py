from django.urls import path
from . import views
from .views import UpdateProfile

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('<int:pk>/update/', UpdateProfile.as_view(), name='profile-update')
]