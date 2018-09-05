from django.contrib.auth import get_user_model
from django.db import models
from oauth2client.contrib.django_util.models import CredentialsField

User = get_user_model()


class UserCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credentials = CredentialsField()
