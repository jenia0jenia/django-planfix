from django.db import models
from django.contrib.auth.models import User

class PlanfixModel(models.Model):
    contact_id = models.IntegerField(null=True, blank=True)
    task_id = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
    )
