from django.db import models


class TestModel(models.Model):
    test_field = models.DateTimeField(null=True, blank=True)
