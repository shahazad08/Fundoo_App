# # from datetime import timezone
# from django.utils import timezone
#
# from django_auth.users.models import User
# # from django.contrib.auth.models import User
# from django.db import models
# class Notes(models.Model):
#     title=models.CharField
#     description=models.TextField()
#     created_time=models.DateTimeField(auto_now_add=True,null=True)
#     reminder=models.DateTimeField(default=timezone.now)
#     is_archived = models.BooleanField(default=False)
#     is_deleted = models.BooleanField(default=False)
#     color = models.CharField(default=None, max_length=50, blank=True, null=True)
#     image = models.ImageField(default=None, null=True)
#     trash = models.BooleanField(default=False)
#     is_pinned = models.NullBooleanField(blank=True, null=True, default=None)
#     label = models.CharField(max_length=50)
#     collaborate = models.ManyToManyField(User, null=True, blank=True, related_name='collaborated_user')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True, blank=True)
#
#     def __str__(self):
#         return self.title
#
#     # def get_absolute_url(self):
#
