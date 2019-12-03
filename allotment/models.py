from django.contrib.auth.models import User
from django.db import models


class Party(models.Model):
    credentials = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key_deadline = models.DateTimeField(null=True, blank=True)
    permutation_number_deadline = models.DateTimeField(null=True, blank=True)


class Participant(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    public_key = models.BinaryField(null=True, blank=True, max_length=64, unique=True)
    permutation_commitment = models.BinaryField(null=True, blank=True, max_length=32)
    permutation_number = models.BinaryField(null=True, blank=True, max_length=32)
    gifter_obj = models.ForeignKey('self', null=True, blank=True, related_name='gifter', on_delete=models.SET_NULL)
    recipient_obj = models.ForeignKey('self', null=True, blank=True, related_name='recipient', on_delete=models.SET_NULL)
    recipient_cipher = models.CharField(max_length=4096)
    recipient_plaintext = models.CharField(max_length=64)

    unique_together = ('party', 'public_key')
