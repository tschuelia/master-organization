from django.urls import path
from . import views
from .views import CourseCreateView, SpecializationCreateView, CourseTypeCreateView

urlpatterns = [
    path('', views.overview, name='overview'),
    #/master/course/5/
    path('course/<int:course_id>/', views.course_detail, name='course-detail'),
    path('course/new', CourseCreateView.as_view(), name='course-create'),
    path('specialization/new', SpecializationCreateView.as_view(), name='specialization-create'),
    path('type/new', CourseTypeCreateView.as_view(), name='type-create')
]