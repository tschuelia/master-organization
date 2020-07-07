from math import floor

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse

MAX_CREDITS_SEM_INT = 18


# The specializations for a course (Vertiefungsfächer)
class Specialization(models.Model):
    specialization_name = models.CharField(
        max_length=100, unique=True, verbose_name="Name"
    )
    specialization_abbreviation = models.CharField(
        max_length=10, unique=True, verbose_name="Abkürzung"
    )

    def __str__(self):
        return self.specialization_name

    def get_absolute_url(self):
        return reverse("overview")

    def get_courses(self, student):
        return (
            StudentCourse.objects.all()
            .filter(course__specializations__contains=self)
            .filter(student=student)
        )

    def get_sum_of_credits(self, student):
        return sum(c.credit_points for c in self.get_courses(student))


# Custom User Model Student
# regular user model extended with major1 and major2
class Student(AbstractUser):
    major1 = models.ForeignKey(
        Specialization,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Vertiefungsfach 1",
        related_name="major1",
    )
    major2 = models.ForeignKey(
        Specialization,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Vertiefungsfach 2",
        related_name="major2",
    )

    def __str__(self):
        return self.username


# The type of a course
class CourseType(models.Model):
    type_name = models.CharField(max_length=30, unique=True, verbose_name="Name")
    type_abbreviation = models.CharField(
        max_length=5, unique=True, verbose_name="Abkürzung"
    )
    min_ects_required = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimal nötige Anzahl ECTS in dieser Kategorie",
    )
    max_ects_creditable = models.IntegerField(
        blank=True, null=True, verbose_name="Maximale Anzahl anrechenbarer ECTS"
    )

    def __str__(self):
        return self.type_name

    def get_absolute_url(self):
        return reverse("overview")

    def get_courses(self, student):
        return (
            StudentCourse.objects.all()
            .filter(course__course_type=self)
            .filter(student=student)
        )

    def get_included_courses(self, student):
        return (
            StudentCourse.objects.all()
            .filter(course__course_type=self)
            .filter(included=True)
            .filter(student=student)
        )

    def get_sum_of_credits(self, student):
        total = sum(c.course.credit_points for c in self.get_included_courses(student))
        return (
            min(self.max_ects_creditable, total) if self.max_ects_creditable else total
        )

    def get_missing_credits(self, student):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits(student))

    def get_possible_credits(self, student):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits(student))

    def is_valid(self, student):
        return self.get_missing_credits(student) == 0

    def get_average(self, student):
        sum_grades = sum(
            c.grade * c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )
        sum_credits_with_grade = sum(
            c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10


# The course itself
class Course(models.Model):
    course_name = models.CharField(max_length=200, verbose_name="Titel")
    credit_points = models.DecimalField(
        max_digits=3, decimal_places=1, default=0, verbose_name="ECTS"
    )
    course_type = models.ForeignKey(
        CourseType,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        verbose_name="Kurstyp",
    )
    specializations = models.ManyToManyField(
        Specialization, blank=True, verbose_name="Vertiefungsfächer laut Modulhandbuch"
    )

    def __str__(self):
        return self.course_name

    def get_credits(self):
        return min(self.category.max_ects_creditable, self.credit_points)

    def get_absolute_url(self):
        return reverse("studentcourse-detail", kwargs={"course_id": self.pk})

    def get_specializations_abbreviations(self):
        l = [c.specialization_abbreviation for c in self.specializations.all()]
        return ", ".join(l)


class Category(models.Model):
    category_name = models.CharField(
        max_length=100, unique=True, verbose_name="Studienteil"
    )
    min_ects_required = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimal nötige Anzahl ECTS in diesem Bereich",
    )
    max_ects_creditable = models.IntegerField(
        blank=True, null=True, verbose_name="Maximale Anzahl anrechenbarer ECTS"
    )

    def __str__(self):
        return self.category_name

    def get_courses(self, student):
        return self.studentcourse_set.all().filter(student=student)

    def get_included_courses(self, student):
        return (
            self.studentcourse_set.all().filter(included=True).filter(student=student)
        )

    def get_included_courses_with_grade(self, student):
        return (
            self.studentcourse_set.all()
            .filter(grade__gt=0)
            .filter(included=True)
            .filter(student=student)
        )

    def get_sum_of_credits_with_grade(self, student):
        total = sum(
            c.course.credit_points
            for c in self.get_included_courses_with_grade(student)
        )
        return (
            min(self.max_ects_creditable, total) if self.max_ects_creditable else total
        )

    def get_sum_of_credits(self, student):
        total = sum(c.course.credit_points for c in self.get_included_courses(student))
        return (
            min(self.max_ects_creditable, total) if self.max_ects_creditable else total
        )

    def get_missing_credits(self, student):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits(student))

    def get_possible_credits(self, student):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits(student))

    def is_valid(self, student):
        return self.get_missing_credits(student) == 0

    def get_average(self, student):
        sum_grades = sum(
            c.grade * c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )
        sum_credits_with_grade = sum(
            c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10


class Semester(models.Model):
    # SS20 oder WS19/20
    term = models.CharField(
        max_length=2, choices=[("SS", "Sommersemester"), ("WS", "Wintersemester")]
    )
    year = models.CharField(max_length=5)

    def __str__(self):
        return self.term + " " + self.year

    def get_courses(self, student):
        return (
            self.studentcourse_set.all().filter(student=student).order_by("exam_date")
        )

    def get_included_courses(self, student):
        return (
            self.studentcourse_set.all().filter(included=True).filter(student=student)
        )

    def get_sum_of_credits(self, student):
        return sum(c.course.credit_points for c in self.get_included_courses(student))

    def get_average(self, student):
        sum_grades = sum(
            c.grade * c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )
        sum_credits_with_grade = sum(
            c.course.credit_points
            for c in self.get_included_courses(student)
            if c.grade > 0
        )

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10


class StudentCourse(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Student"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Kurs")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=False, verbose_name="Kategorie",
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, null=False, verbose_name="Prüfungssemester",
    )
    exam_date = models.DateTimeField(
        verbose_name="Prüfungstermin", blank=True, null=True
    )
    grade = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True,
        default=0,
        verbose_name="Note",
    )
    included = models.BooleanField(
        default=True, verbose_name="In Berechnung mit einbeziehen?"
    )

    def __str__(self):
        return f"{self.course} ({self.student})"


def get_total_credits(student):
    categories = Category.objects.all()
    return sum(c.get_sum_of_credits(student) for c in categories)


def get_total_credits_passed(student):
    categories = Category.objects.all()
    return sum(c.get_sum_of_credits_with_grade(student) for c in categories)


def get_total_average(student):
    categories = Category.objects.all()
    sum_credits = sum(
        c.course.credit_points
        for cat in categories
        for c in cat.get_included_courses(student)
        if c.grade > 0
    )
    total_grades = sum(
        c.grade * c.course.credit_points
        for cat in categories
        for c in cat.get_included_courses(student)
        if c.grade > 0
    )
    if sum_credits <= 0:
        return 0
    return floor(10 * (total_grades / sum_credits)) / 10


def get_credits_sem_int(student):
    internships = get_object_or_404(CourseType, type_name="Praktikum")
    seminars = get_object_or_404(CourseType, type_name="Seminar")

    return internships.get_sum_of_credits(student) + seminars.get_sum_of_credits(
        student
    )


def get_missing_credits_sem_int(student):
    internships = get_object_or_404(CourseType, type_name="Praktikum")
    seminars = get_object_or_404(CourseType, type_name="Seminar")

    missing_int = internships.get_missing_credits(student)
    missing_sem = seminars.get_missing_credits(student)

    return missing_int + missing_sem


def course_not_creditable(course, included, student):
    # course is not creditable if it is an internship or a seminar
    # and it should be included in the calculations
    # and the student has already included 18 or more seminar/internship credits
    is_seminar_or_internship = (
        course.course_type.type_name == "Praktikum"
        or course.course_type.type_name == "Seminar"
    )
    return is_seminar_or_internship and included and get_credits_sem_int(student) >= 18
