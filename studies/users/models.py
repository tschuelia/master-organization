from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    major1 = models.ForeignKey('master.specialization', blank=True, null=True, default=None, on_delete=models.SET_NULL, verbose_name='Vertiefungsfach 1', related_name='major1')
    major2 = models.ForeignKey('master.specialization', blank=True, null=True, default=None, on_delete=models.SET_NULL, verbose_name='Vertiefungsfach 2', related_name='major2')

    def __str__(self):
        return self.user.username
