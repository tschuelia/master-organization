from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from math import floor

MAX_CREDITS_SEM_INT = 18

# The type of a course
class CourseType(models.Model):
    type_name = models.CharField(max_length=30,  unique=True, verbose_name='Name')
    type_abbreviation = models.CharField(max_length=5,  unique=True, verbose_name='Abkürzung')
    min_ects_required = models.IntegerField(blank=True, null=True, verbose_name='Minimal nötige Anzahl ECTS in dieser Kategorie')
    max_ects_creditable = models.IntegerField(blank=True, null=True, verbose_name='Maximale Anzahl anrechenbarer ECTS')

    def __str__(self):
        return self.type_name
    
    def get_absolute_url(self):
        return reverse('overview')
    
    def get_courses(self, user):
        return UserCourse.objects.all().filter(course__course_type=self).filter(user=user)
    
    def get_included_courses(self, user):
        return UserCourse.objects.all().filter(course__course_type=self).filter(included=True).filter(user=user)
    
    def get_sum_of_credits(self, user):
        total = sum(c.course.credit_points for c in self.get_included_courses(user))
        return min(self.max_ects_creditable, total) if self.max_ects_creditable else total
    
    def get_missing_credits(self, user):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits(user))
    
    def get_possible_credits(self, user):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits(user))
    
    def is_valid(self, user):
        return self.get_missing_credits(user) == 0
    
    def get_average(self, user):
        sum_grades = sum(c.grade * c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)
        sum_credits_with_grade = sum(c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10


# The specializations for a course (Vertiefungsfächer)
class Specialization(models.Model):
    specialization_name = models.CharField(max_length=100,  unique=True, verbose_name='Name')
    specialization_abbreviation = models.CharField(max_length=10, unique=True, verbose_name='Abkürzung')

    def __str__(self):
        return '{} ({})'.format(self.specialization_name, self.specialization_abbreviation)

    def get_absolute_url(self):
        return reverse('overview')
    
    def get_courses(self, user):
        return UserCourse.objects.all().filter(course__specializations__contains=self).filter(user=user)


    def get_sum_of_credits(self, user):
        return sum(c.credit_points for c in self.get_courses(user))

# The course itself
class Course(models.Model):
    course_name = models.CharField(max_length=200, verbose_name='Titel')
    credit_points = models.IntegerField(default=0, verbose_name='ECTS')
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Kurstyp')
    specializations = models.ManyToManyField(Specialization, blank=True, verbose_name='Vertiefungsfächer laut Modulhandbuch')
    #category = models.ForeignKey(Category, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Kategorie')
    #semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Prüfungssemester')
    #grade = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, default=0, verbose_name='Note')
    #included = models.BooleanField(default=True, verbose_name='In Berechnung mit einbeziehen?')

    def __str__(self):
        return self.course_name
    
    
    def get_credits(self):
        return min(self.category.max_ects_creditable, self.credit_points)

    
    def get_absolute_url(self):
        return reverse('course-detail', kwargs={'course_id': self.pk})
    
    def get_specializations_abbreviations(self):
        l =  [c.specialization_abbreviation for c in self.specializations.all()]
        return ', '.join(l)

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True, verbose_name='Studienteil')
    min_ects_required = models.IntegerField(blank=True, null=True, verbose_name='Minimal nötige Anzahl ECTS in diesem Bereich')
    max_ects_creditable = models.IntegerField(blank=True, null=True, verbose_name='Maximale Anzahl anrechenbarer ECTS')

    def __str__(self):
        return self.category_name
    
    def get_courses(self, user):
        return self.usercourse_set.all().filter(user=user)
    
    def get_included_courses(self,user):
        return self.usercourse_set.all().filter(included=True).filter(user=user)
    
    def get_sum_of_credits(self, user):
        total = sum(c.course.credit_points for c in self.get_included_courses(user))
        return min(self.max_ects_creditable, total) if self.max_ects_creditable else total

    def get_missing_credits(self, user):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits(user))
    
    def get_possible_credits(self, user):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits(user))
    
    def is_valid(self, user):
        return self.get_missing_credits(user) == 0
    
    def get_average(self, user):
        sum_grades = sum(c.grade * c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)
        sum_credits_with_grade = sum(c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10

class Semester(models.Model):
    # SS20 oder WS19/20
    term = models.CharField(max_length=2, choices=[('SS', 'Sommersemester'), ('WS', 'Wintersemester')])
    year = models.CharField(max_length=5)

    def __str__(self):
        return self.term + ' ' + self.year
    
    def get_courses(self, user):
        return self.usercourse_set.all().filter(user=user)
    
    def get_included_courses(self, user):
        return self.usercourse_set.all().filter(included=True).filter(user=user)
    
    def get_sum_of_credits(self, user):
        return sum(c.course.credit_points for c in self.get_included_courses(user))
    
    def get_average(self, user):
        sum_grades = sum(c.grade * c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)
        sum_credits_with_grade = sum(c.course.credit_points for c in self.get_included_courses(user) if c.grade > 0)

        if sum_credits_with_grade <= 0:
            return 0

        return floor(10 * (sum_grades / sum_credits_with_grade)) / 10

class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Student')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Kurs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Kategorie')
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Prüfungssemester')
    grade = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, default=0, verbose_name='Note')
    included = models.BooleanField(default=True, verbose_name='In Berechnung mit einbeziehen?')

    def __str__(self):
        return f'{self.course} ({self.user})'
    

def get_total_credits(user):
    categories = Category.objects.all()
    return sum(c.get_sum_of_credits(user) for c in categories)

def get_total_average(user):
    categories = Category.objects.all()
    sum_credits = sum(c.course.credit_points for cat in categories for c in cat.get_included_courses(user) if c.grade > 0)
    total_grades = sum(c.grade * c.course.credit_points for cat in categories for c in cat.get_included_courses(user) if c.grade > 0)
    if sum_credits <= 0:
        return 0
    return floor(10 * (total_grades / sum_credits)) / 10
