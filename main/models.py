import uuid
from django.db import models

# Create your models here.

class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    chain = models.CharField(max_length=1, null=True)
    ph = models.DecimalField(max_digits=3, decimal_places=1)
    ph_range = models.BooleanField()
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    submit_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()

    def __str__(self):
        return '<Job (%r) - %r>' % (self.id, self.name)
