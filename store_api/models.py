from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    opening_hours = models.CharField(max_length=100)

    def __str__(self):
        return self.name
