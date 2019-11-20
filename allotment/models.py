from django.contrib.auth.models import User
from django.db import models


class Party(models.Model)
    credentials = models.OneToOneField(User, on_delete=models.CASCADE)


class Deadlines(models.Model):
    party = models.OneToOneField(Party, on_delete=models.CASCADE)
    public_key = model.DateTimeField()
    permutation_number_verify = model.DateTimeField()


class Participant(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    public_key = models.BinaryField(null=True, blank=True, max_length=32)
    permutation_number_hash = models.BinaryField(null=True, blank=True, max_length=32)
    permutation_number = models.BinaryField(null=True, blank=True, max_length=32)
    gifter = models.ForeignKey(self, null=True, blank=True)
    recipient = models.ForeignKey(self, null=True, blank=True)
