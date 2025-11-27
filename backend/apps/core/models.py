import uuid
from django.db import models


class User(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.TextField()
    first_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True, blank=True)
    role = models.TextField(default='user')
    department = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.username


class Event(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    type = models.TextField()
    payload = models.TextField()
    status = models.TextField(default='pending')
    source = models.TextField()
    processed_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'
        managed = False


class AuditLog(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='user_id')
    action = models.TextField()
    entity_type = models.TextField()
    entity_id = models.TextField()
    old_values = models.TextField(null=True, blank=True)
    new_values = models.TextField(null=True, blank=True)
    ip_address = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        managed = False
