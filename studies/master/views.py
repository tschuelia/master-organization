from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_addanother.views import CreatePopupMixin

from .forms import StudentCourseForm
from .models import (
    Category,
    Course,
    CourseType,
    Semester,
    Specialization,
    Student,
    StudentCourse,
    course_not_creditable,
    get_credits_sem_int,
    get_missing_credits_sem_int,
    get_total_average,
    get_total_credits,
    get_total_credits_passed,
)


def accumulate_information_for_category(category, student):
    cat = get_object_or_404(Category, category_name=category)
    return {
        "courses": cat.get_courses(student),
        "is_valid": cat.is_valid(student),
        "sum_of_credits": cat.get_sum_of_credits(student),
        "missing_credits": cat.get_missing_credits(student),
        "possible_credits": cat.get_possible_credits(student),
        "average": cat.get_average(student),
    }


def accumulate_information_for_coursetype(course_type, student):
    ct = get_object_or_404(CourseType, type_name=course_type)
    return {
        "courses": ct.get_courses(student),
        "is_valid": ct.is_valid(student),
        "sum_of_credits": ct.get_sum_of_credits(student),
        "missing_credits": ct.get_missing_credits(student),
        "possible_credits": ct.get_possible_credits(student),
        "average": ct.get_average(student),
    }


@login_required
def overview(request):
    student = request.user

    internship = accumulate_information_for_coursetype("Praktikum", student)
    seminar = accumulate_information_for_coursetype("Seminar", student)

    sum_credits_int_sem = get_credits_sem_int(student)
    missing_int_sem = get_missing_credits_sem_int(student)
    seminars_and_internships_valid = missing_int_sem == 0

    params = {
        "student": student,
        "total_credits": get_total_credits(student),
        "total_credits_passed": get_total_credits_passed(student),
        "total_missing_credits": 90 - get_total_credits(student),
        "total_average": get_total_average(student),
        "major1": accumulate_information_for_category("Vertiefungsfach 1", student),
        "major2": accumulate_information_for_category("Vertiefungsfach 2", student),
        "minor": accumulate_information_for_category("Ergänzungsfach", student),
        "electives": accumulate_information_for_category("Wahlbereich", student),
        "soft_skills": accumulate_information_for_category(
            "Schlüsselqualifikation", student
        ),
        "internships": internship,
        "seminars": seminar,
        "sum_credits_int_sem": sum_credits_int_sem,
        "missing_int_sem": missing_int_sem,
        "seminars_and_internships_valid": seminars_and_internships_valid,
        "base_modules": accumulate_information_for_coursetype("Stammmodul", student),
    }

    return render(request, "master/overview.html", params)


@login_required
def semesters(request):
    student = request.user
    semesters = Semester.objects.all()
    semesters.order_by("year")

    # (sem, {courses:[], credits:[]}), (sem2, {courses:[]})
    params = []
    for sem in semesters:
        var = {
            "courses": sem.get_courses(student),
            "credits": sem.get_sum_of_credits(student),
            "average": sem.get_average(student),
        }
        params.append((sem, var))

    return render(request, "master/semester_view.html", {"params": params})


@login_required
def exam_date_view(request):
    student = request.user
    semesters = Semester.objects.all()
    semesters.order_by("year")

    params = []
    for sem in semesters:
        courses = sem.get_courses(student)
        params.append((sem, courses))

    return render(
        request, "master/exam_dates.html", {"params": params, "now": timezone.now()}
    )


# Course details
@login_required
def studentcourse_detail(request, course_id):
    studentcourse = get_object_or_404(StudentCourse, pk=course_id)
    return render(
        request,
        "master/studentcourse_detail.html",
        {
            "studentcourse": studentcourse,
            "specializations": studentcourse.course.specializations.all(),
        },
    )


@login_required
def confirm_studentcourse(request, course_id):
    if request.method == "GET":
        studentcourse = get_object_or_404(StudentCourse, pk=course_id)
        return render(
            request,
            "master/confirm_studentcourse.html",
            {"studentcourse": studentcourse},
        )
    else:
        studentcourse = get_object_or_404(StudentCourse, pk=course_id)
        studentcourse.included = False
        studentcourse.save()
        return redirect("studentcourse-detail", course_id=studentcourse.pk)


class StudentCourseCreateView(LoginRequiredMixin, CreateView):
    model = StudentCourse
    form_class = StudentCourseForm

    def form_valid(self, form):
        form.instance.student = self.request.user
        self.object = form.save()
        if course_not_creditable(
            self.object.course, self.object.included, self.request.user
        ):
            # no more seminars/internships creditable
            return redirect("studentcourse-confirm", course_id=self.object.pk)

        return redirect("studentcourse-detail", course_id=self.object.pk)


class StudentCourseUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentCourse
    form_class = StudentCourseForm

    def form_valid(self, form):
        form.instance.student = self.request.user
        self.object = form.save()
        if course_not_creditable(
            self.object.course, self.object.included, self.request.user
        ):
            # no more seminars/internships creditable
            return redirect("studentcourse-confirm", course_id=self.object.pk)

        return redirect("studentcourse-detail", course_id=self.object.pk)


class StudentCourseDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentCourse
    success_url = "/"


class SpecializationCreateView(LoginRequiredMixin, CreateView):
    model = Specialization
    fields = "__all__"


class CourseTypeCreateView(LoginRequiredMixin, CreateView):
    model = CourseType
    fields = "__all__"


class CourseCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Course
    fields = "__all__"


@login_required
def student_view(request):
    return render(request, "master/student.html", {"student": request.user})


class UpdateStudent(LoginRequiredMixin, UpdateView):
    model = Student
    fields = ["major1", "major2"]
    success_url = "/student"
