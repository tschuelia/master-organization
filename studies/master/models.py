from django.db import models
from django.urls import reverse

# The type of a course
class CourseType(models.Model):
    type_name = models.CharField(max_length=20)
    type_abbreviation = models.CharField(max_length=5)

    def __str__(self):
        return '{} ({})'.format(self.type_name, self.type_abbreviation)
    
    def get_absolute_url(self):
        return reverse('overview')


# The categories for a course (Vertiefungsfächer)
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return '{} ({})'.format(self.category_name, self.category_abbreviation)

    def get_absolute_url(self):
        return reverse('overview')
    

# The course itself
class Course(models.Model):
    course_name = models.CharField(max_length=200, verbose_name='CourseName')
    credit_points = models.IntegerField(default=0, verbose_name='CreditPoints')
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, default=None, null=True, verbose_name='CourseType')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='Categories')

    def __str__(self):
        return self.course_name
    

    def get_absolute_url(self):
        return reverse('course-detail', kwargs={'course_id': self.pk})
    