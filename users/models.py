from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('cashier', 'Кассир'),
        ('admin', 'Админ'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='cashier')
