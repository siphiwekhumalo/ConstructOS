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
    planned_progress = models.IntegerField(default=0, help_text="Expected progress percentage based on schedule")
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Actual cost to date")
    due_date = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='manager_id')
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    next_milestone_date = models.DateField(null=True, blank=True, help_text="Date of next project milestone")
    next_milestone_name = models.TextField(null=True, blank=True, help_text="Name of next project milestone")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
    
    @property
    def progress_variance(self):
        """Calculate progress variance (actual - planned). Negative = behind schedule."""
        return self.progress - self.planned_progress
    
    @property
    def cost_variance(self):
        """Calculate cost variance (budget - actual). Negative = over budget."""
        return float(self.budget) - float(self.actual_cost)
    
    @property
    def health_status(self):
        """Determine project health based on progress variance."""
        variance = self.progress_variance
        if variance >= 0:
            return 'on_track'
        elif variance >= -5:
            return 'at_risk'
        else:
            return 'delayed'


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
