from django.urls import path
from . import views
from .views import (
    UserCourseCreateView, 
    SpecializationCreateView, 
    CourseTypeCreateView, 
    UserCourseUpdateView,
    UserCourseDeleteView
)

urlpatterns = [
    path('', views.overview, name='overview'),
    path('semesterview', views.semesters, name='semester-view'),
    #/master/course/5/
    path('course/<int:course_id>/', views.usercourse_detail, name='course-detail'),
    path('course/new/', UserCourseCreateView.as_view(), name='course-create'),
    path('course/<int:course_id>/confirm/', views.confirm_usercourse, name='course-confirm'),
    path('course/<int:pk>/update/', UserCourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', UserCourseDeleteView.as_view(), name='course-delete'),
    path('specialization/new/', SpecializationCreateView.as_view(), name='specialization-create'),
    path('type/new/', CourseTypeCreateView.as_view(), name='type-create')
]