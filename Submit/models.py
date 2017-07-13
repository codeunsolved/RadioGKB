from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class Draft(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Under Review', 'Under Review'),
        ('Revision', 'Revision'),
        ('Accepted', ' Accepted'),
        ('Rejected', 'Rejected'),)

    KB_CHOICES = (
        ('SNP', 'SNP'),
        ('Expression', 'Expression'),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=STATUS_CHOICES)
    kb = models.CharField(max_length=20, choices=KB_CHOICES)
    pubmed_id = models.IntegerField()
    content = JSONField()

    def __str__(self):
        return "{!s} | {} | {} | {}".format(self.user, self.state, self.kb, self.pubmed_id)
