from django.urls import path

from . import views
from .views import (
    CourseTypeCreateView,
    SpecializationCreateView,
    StudentCourseCreateView,
    StudentCourseDeleteView,
    StudentCourseUpdateView,
    UpdateStudent,
)

urlpatterns = [
    path("", views.overview, name="overview"),
    path("semesterview", views.semesters, name="semester-view"),
    # /master/course/5/
    path("course/<int:course_id>", views.studentcourse_detail, name="course-detail"),
    path("course/new/", StudentCourseCreateView.as_view(), name="course-create"),
    path(
        "course/<int:course_id>/confirm",
        views.confirm_studentcourse,
        name="course-confirm",
    ),
    path(
        "course/<int:pk>/update",
        StudentCourseUpdateView.as_view(),
        name="course-update",
    ),
    path(
        "course/<int:pk>/delete",
        StudentCourseDeleteView.as_view(),
        name="course-delete",
    ),
    path("student/", views.student_view, name="student"),
    path("student/<int:pk>/update", UpdateStudent.as_view(), name="student-update"),
    path(
        "specialization/new",
        SpecializationCreateView.as_view(),
        name="specialization-create",
    ),
    path("type/new", CourseTypeCreateView.as_view(), name="type-create"),
]
