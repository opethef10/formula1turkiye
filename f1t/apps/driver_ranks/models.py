from django.db import models
from django.contrib.auth.models import User

from f1t.apps.fantasy.models import Driver, Championship

class PollResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
