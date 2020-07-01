from django.urls import path

from . import views
from .views import (
    CourseCreateView,
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
    path(
        "studentcourse/<int:course_id>",
        views.studentcourse_detail,
        name="studentcourse-detail",
    ),
    path(
        "studentcourse/new/",
        StudentCourseCreateView.as_view(),
        name="studentcourse-create",
    ),
    path(
        "studentcourse/<int:course_id>/confirm",
        views.confirm_studentcourse,
        name="studentcourse-confirm",
    ),
    path(
        "studentcourse/<int:pk>/update",
        StudentCourseUpdateView.as_view(),
        name="studentcourse-update",
    ),
    path(
        "studentcourse/<int:pk>/delete",
        StudentCourseDeleteView.as_view(),
        name="studentcourse-delete",
    ),
    path("student/", views.student_view, name="student"),
    path("student/<int:pk>/update", UpdateStudent.as_view(), name="student-update"),
    path("course/new", CourseCreateView.as_view(), name="course-create"),
    path(
        "specialization/new",
        SpecializationCreateView.as_view(),
        name="specialization-create",
    ),
    path("type/new", CourseTypeCreateView.as_view(), name="type-create"),
]
