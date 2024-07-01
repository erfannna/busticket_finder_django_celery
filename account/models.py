from django.db import models
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    username, date_joined = None, None
    phone_number = models.PositiveIntegerField(blank=False,
                                               unique=True)
    subscription = models.BooleanField(default=False)
    sub_expire_date = models.DateTimeField(default=timezone.now)
    sub_type = models.PositiveSmallIntegerField(default=1)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)


class Service(models.Model):
    name = models.CharField(blank=False,
                            max_length=200)
    datetime = models.DateField(blank=True)
    checking_url = models.URLField(blank=False)
    expired = models.BooleanField(default=False)
    passengers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='service_passengers',
                                        blank=True)

    def __str__(self):
        return str(self.name)


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='user_payments',
                             on_delete=models.CASCADE)
    price = models.PositiveIntegerField(blank=False)
    description = models.CharField(max_length=200,
                                   blank=False)
    status = models.CharField(max_length=50,
                              blank=False)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.description)


class InformReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='user_sms_report',
                             on_delete=models.CASCADE)
    service = models.ForeignKey(Service,
                                related_name='service_sms_report',
                                on_delete=models.CASCADE)
    type = models.CharField(max_length=10,
                            blank=False)
    status = models.CharField(max_length=50,
                              blank=False)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.status)
