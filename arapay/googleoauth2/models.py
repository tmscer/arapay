from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.fields.TextField
    refresh_token = models.fields.TextField
    last_refreshed = models.fields.DateTimeField
    expires_in_seconds = models.fields.IntegerField
