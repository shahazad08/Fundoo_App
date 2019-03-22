from __future__ import unicode_literals
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given name must be set")
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(self._db)
                return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):  # User model is the built-in Django model that provides
    # us with username , email , password , first_name , and last_name fields.
    # username=models.(max_length=40,unique=True)
    email = models.EmailField(max_length=40, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default=None, null=True)
    object = UserManager()  # Created the object of the User Manager module which contains the fields..

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self


class CreateNotes(models.Model):
    title = models.CharField(max_length=150,default=None)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    remainder = models.DateTimeField(default=None, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    color = models.CharField(default=None, max_length=50, blank=True, null=True)
    image = models.ImageField(default=None, null=True)
    trash = models.BooleanField(default=False)
    is_pinned = models.NullBooleanField(blank=True,default=False)
    label = models.CharField(max_length=50,default=None,null=True)
    collaborate = models.ManyToManyField(User, null=True, blank=True, related_name='collaborated_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True, blank=True)

    def __str__(self):
        return self.title

class Labels(models.Model):
    label_name = models.CharField(max_length=150)
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.label_name

class MapLabel(models.Model):
    note_id = models.ForeignKey(CreateNotes, on_delete=models.CASCADE,null=True, blank=True,db_constraint=False)
    label_id = models.ForeignKey(Labels, on_delete=models.CASCADE,null=True, blank=True,db_constraint=False)
    created_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.note_id)