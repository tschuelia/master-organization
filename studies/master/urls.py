from django.urls import path
from . import views
from .views import (
    CourseCreateView, 
    SpecializationCreateView, 
    CourseTypeCreateView, 
    CourseUpdateView,
    CourseDeleteView
)

urlpatterns = [
    path('', views.overview, name='overview'),
    path('semesterview', views.semesters, name='semester-view'),
    #/master/course/5/
    path('course/<int:course_id>/', views.course_detail, name='course-detail'),
    path('course/new/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:course_id>/confirm/', views.confirm_course, name='course-confirm'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('specialization/new/', SpecializationCreateView.as_view(), name='specialization-create'),
    path('type/new/', CourseTypeCreateView.as_view(), name='type-create')
]