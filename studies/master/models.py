from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404

MAJOR1 = 'KogSys'
MAJOR2 = 'Para'


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
    
    def get_courses(self):
        return self.course_set.all()
    
    def get_sum_of_credits(self):
        return sum(c.credit_points for c in self.get_courses())
    
    def get_missing_credits(self):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits())
    
    def get_possible_credits(self):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits())


# The specializations for a course (Vertiefungsfächer)
class Specialization(models.Model):
    specialization_name = models.CharField(max_length=100,  unique=True, verbose_name='Name')
    specialization_abbreviation = models.CharField(max_length=10, unique=True, verbose_name='Abkürzung')

    def __str__(self):
        return '{} ({})'.format(self.specialization_name, self.specialization_abbreviation)

    def get_absolute_url(self):
        return reverse('overview')


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True, verbose_name='Studienteil')
    min_ects_required = models.IntegerField(blank=True, null=True, verbose_name='Minimal nötige Anzahl ECTS in diesem Bereich')
    max_ects_creditable = models.IntegerField(blank=True, null=True, verbose_name='Maximale Anzahl anrechenbarer ECTS')

    def __str__(self):
        return self.category_name
    
    def get_courses(self):
        return self.course_set.all()
    
    def get_sum_of_credits(self):
        return sum(c.credit_points for c in self.get_courses())
    
    def get_missing_credits(self):
        if not self.min_ects_required:
            return -1
        return max(0, self.min_ects_required - self.get_sum_of_credits())
    
    def get_possible_credits(self):
        if not self.max_ects_creditable:
            return -1
        return max(0, self.max_ects_creditable - self.get_sum_of_credits())

    

# The course itself
class Course(models.Model):
    course_name = models.CharField(max_length=200, verbose_name='Titel')
    credit_points = models.IntegerField(default=0, verbose_name='ECTS')
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Kurstyp')
    specializations = models.ManyToManyField(Specialization, blank=True, verbose_name='Vertiefungsfächer laut Modulhandbuch')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, default=None, null=True, verbose_name='Kategorie')

    def __str__(self):
        return self.course_name
    

    def get_absolute_url(self):
        return reverse('course-detail', kwargs={'course_id': self.pk})
    
    def get_specializations_abbreviations(self):
        l =  [c.specialization_abbreviation for c in self.specializations.all()]
        return ', '.join(l)
