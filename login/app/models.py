from django.db import models

# Create your models here.

class Userinfo(models.Model):
  user_name = models.CharField(max_length=255, primary_key=True)
  password = models.CharField(max_length=1550)
  role_type = models.IntegerField()
  class Meta:
    db_table = 'userinfo'

class Security(models.Model):
  session_id = models.AutoField(primary_key=True)
  user_name = models.CharField(max_length=255)
  auth_key = models.CharField(max_length=255)
  role_type = models.IntegerField()
  class Meta:
    db_table = 'security'
