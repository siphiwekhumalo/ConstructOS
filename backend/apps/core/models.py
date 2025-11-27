import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    """
    User model with comprehensive RBAC support for ConstructOS.
    Supports 11 distinct roles with different access levels.
    """
    ROLE_CHOICES = [
        ('system_admin', 'System Administrator'),
        ('finance_manager', 'Finance Manager'),
        ('sales_rep', 'Sales Representative'),
        ('operations_specialist', 'Operations Specialist'),
        ('site_manager', 'Site Manager'),
        ('hr_specialist', 'HR Specialist'),
        ('warehouse_clerk', 'Warehouse Clerk'),
        ('field_worker', 'Field Worker'),
        ('subcontractor', 'Subcontractor/Vendor'),
        ('client', 'Client/Customer'),
        ('executive', 'Executive Viewer'),
    ]
    
    USER_TYPE_CHOICES = [
        ('internal', 'Internal Staff'),
        ('external', 'External User'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password_hash = models.TextField(blank=True, default='')
    first_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True, blank=True)
    role = models.TextField(default='field_worker', choices=ROLE_CHOICES)
    user_type = models.TextField(default='internal', choices=USER_TYPE_CHOICES)
    department = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    azure_ad_object_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    azure_ad_roles = models.JSONField(default=list, blank=True)
    
    assigned_warehouse_id = models.CharField(max_length=255, null=True, blank=True)
    assigned_project_ids = models.JSONField(default=list, blank=True)
    assigned_account_ids = models.JSONField(default=list, blank=True)
    vendor_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    @property
    def roles(self):
        roles = [self.role]
        if self.azure_ad_roles:
            roles.extend(self.azure_ad_roles)
        return list(set(roles))
    
    def has_role(self, role):
        return role in self.roles
    
    def has_any_role(self, roles_list):
        return any(role in self.roles for role in roles_list)
    
    @property
    def is_admin(self):
        return self.role == 'system_admin'
    
    @property
    def is_executive(self):
        return self.role in ['system_admin', 'executive']
    
    @property
    def is_internal(self):
        return self.user_type == 'internal'
    
    @property
    def is_external(self):
        return self.user_type == 'external'
    
    def can_access_project(self, project_id):
        if self.is_admin or self.is_executive:
            return True
        if self.role in ['operations_specialist', 'finance_manager', 'hr_specialist']:
            return True
        return str(project_id) in [str(p) for p in self.assigned_project_ids]
    
    def can_access_account(self, account_id):
        if self.is_admin or self.is_executive:
            return True
        if self.role in ['sales_rep', 'finance_manager', 'operations_specialist']:
            return True
        return str(account_id) in [str(a) for a in self.assigned_account_ids]
    
    def can_access_warehouse(self, warehouse_id):
        if self.is_admin or self.is_executive:
            return True
        if self.role == 'operations_specialist':
            return True
        if self.role == 'warehouse_clerk':
            return str(warehouse_id) == str(self.assigned_warehouse_id)
        return False


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


class Favorite(models.Model):
    """
    User favorites for quick access to frequently used records.
    """
    ENTITY_TYPES = [
        ('account', 'Account'),
        ('contact', 'Contact'),
        ('product', 'Product'),
        ('order', 'Sales Order'),
        ('ticket', 'Ticket'),
        ('project', 'Project'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='favorites')
    entity_type = models.TextField(choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=255)
    entity_title = models.TextField()
    entity_subtitle = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'entity_type', 'entity_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.entity_type}: {self.entity_title}"
