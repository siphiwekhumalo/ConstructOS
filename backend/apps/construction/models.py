import uuid
from django.db import models
from backend.apps.core.models import User
from backend.apps.crm.models import Account
from backend.apps.erp.models import Warehouse, Employee


class Project(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    location = models.TextField()
    status = models.TextField()
    progress = models.IntegerField(default=0)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='manager_id')
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        managed = False


class Transaction(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, db_column='project_id')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.TextField()
    category = models.TextField(null=True, blank=True)
    type = models.TextField(default='expense')
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        managed = False


class Equipment(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    status = models.TextField()
    location = models.TextField()
    next_service = models.TextField()
    image_url = models.TextField(null=True, blank=True)
    serial_number = models.TextField(null=True, blank=True)
    purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, db_column='warehouse_id')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, db_column='assigned_to_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        managed = False


class SafetyInspection(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    site = models.TextField()
    type = models.TextField()
    status = models.TextField()
    inspector = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, db_column='project_id')
    findings = models.TextField(null=True, blank=True)
    corrective_actions = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'safety_inspections'
        managed = False


class Document(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    type = models.TextField()
    size = models.TextField()
    author = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, db_column='project_id')
    category = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    version = models.IntegerField(default=1)

    class Meta:
        db_table = 'documents'
        managed = False
