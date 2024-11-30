
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Customer

def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

post_save.connect(create_customer, sender=User)
