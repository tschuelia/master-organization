from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile


def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'users/profile.html', 
        {
            'user': request.user,
            'profile': profile
        })

class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['major1', 'major2']
    success_url = '/student'