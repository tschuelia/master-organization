from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    get_total_credits,
    get_total_average,
    Course, 
    UserCourse,
    Specialization, 
    CourseType, 
    Category, 
    Semester
)
from django.urls import reverse_lazy

def accumulate_information_for_category(category, user):
    cat = get_object_or_404(Category, category_name=category)
    return {
        'courses': cat.get_courses(user),
        'is_valid': cat.is_valid(user),
        'sum_of_credits': cat.get_sum_of_credits(user),
        'missing_credits': cat.get_missing_credits(user),
        'possible_credits': cat.get_possible_credits(user),
        'average': cat.get_average(user)
    }

def accumulate_information_for_coursetype(course_type, user):
    ct = get_object_or_404(CourseType, type_name=course_type)
    return {
        'courses': ct.get_courses(user),
        'is_valid': ct.is_valid(user),
        'sum_of_credits': ct.get_sum_of_credits(user),
        'missing_credits': ct.get_missing_credits(user),
        'possible_credits': ct.get_possible_credits(user),
        'average': ct.get_average(user)
    }

@login_required
def overview(request):
    user = request.user
    specs = Specialization.objects.all()

    internship = accumulate_information_for_coursetype('Praktikum', user)
    seminar = accumulate_information_for_coursetype('Seminar', user)

    sum_credits_int_sem = internship['sum_of_credits'] + seminar['sum_of_credits']
    missing_int_sem = max(0, 12 - sum_credits_int_sem)
    seminars_and_internships_valid = missing_int_sem == 0

    params = {
        'specs': specs,
        'total_credits': get_total_credits(user),
        'total_missing_credits': 90 - get_total_credits(user),
        'total_average': get_total_average(user),
        'major1' : accumulate_information_for_category('Vertiefungsfach 1', user),
        'major2' : accumulate_information_for_category('Vertiefungsfach 2', user),
        'minor' : accumulate_information_for_category('Ergänzungsfach', user),
        'electives':  accumulate_information_for_category('Wahlbereich', user),
        'soft_skills': accumulate_information_for_category('Schlüsselqualifikation', user),
        'internships': internship,
        'seminars': seminar,
        'sum_credits_int_sem': sum_credits_int_sem,
        'missing_int_sem': missing_int_sem,
        'seminars_and_internships_valid': seminars_and_internships_valid,
        'base_modules': accumulate_information_for_coursetype('Stammmodul', user)
    }

    return render(request, 'master/overview.html', params)

@login_required
def semesters(request):
    user = request.user
    semesters = Semester.objects.all()
    semesters.order_by('year')

    #(sem, {courses:[], credits:[]}), (sem2, {courses:[]})
    params = []
    for sem in semesters:
        var = {
            'courses': sem.get_courses(user),
            'credits': sem.get_sum_of_credits(user),
            'average': sem.get_average(user),   
        }
        params.append((sem, var))
    
    return render(request, 'master/semester_view.html', {'params': params})

# Course details
@login_required
def usercourse_detail(request, course_id):
    usercourse = get_object_or_404(UserCourse, pk=course_id)
    return render(request, 'master/usercourse_detail.html', {'usercourse': usercourse, 'specializations': usercourse.course.specializations.all()})

@login_required
def confirm_usercourse(request, course_id):
    if request.method == 'GET':
        course = get_object_or_404(Course, pk=course_id)
        return render(request, 'master/confirm_course.html', {'course': course})
    else:
        course = get_object_or_404(Course, pk=course_id)
        course.included = False
        course.save()
        return redirect('course-detail', course_id=course.pk)

class UserCourseCreateView(LoginRequiredMixin, CreateView):
    model = UserCourse
    fields = ['course', 'category', 'semester', 'grade', 'included']

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        if (self.object.course.course_type.type_name == 'Praktikum' \
            or self.object.course.course_type.type_name == 'Seminar') \
            and self.object.included \
            and get_credits_sem_int(self.request.user) >= 18:
                # no more seminars/internships creditable
                return redirect('course-confirm', course_id=self.object.pk)
                
        return redirect('course-detail', course_id=self.object.pk)

class UserCourseUpdateView(LoginRequiredMixin, UpdateView):
    model = UserCourse
    fields = ['course', 'category', 'semester', 'grade', 'included']

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        if (self.object.course.course_type.type_name == 'Praktikum' \
            or self.object.course.course_type.type_name == 'Seminar') \
            and self.object.included \
            and get_credits_sem_int(self.request.user) >= 18:
                # no more seminars/internships creditable
                return redirect('course-confirm', course_id=self.object.pk)
                
        return redirect('course-detail', course_id=self.object.pk)

class UserCourseDeleteView(LoginRequiredMixin, DeleteView):
    model = UserCourse
    success_url = ''

class SpecializationCreateView(CreateView):
    model = Specialization
    fields = '__all__'

class CourseTypeCreateView(CreateView):
    model = CourseType
    fields = '__all__'
