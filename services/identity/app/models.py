"""
Identity/Contact Service Models

This service owns:
- Users (authentication and authorization)
- Accounts (customers, vendors, partners)
- Contacts (individuals linked to accounts)
- Addresses (physical addresses for accounts/contacts)
- Audit Logs (user activity tracking)
- Favorites (user preferences)
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user model with Azure AD integration."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('finance', 'Finance User'),
        ('hr', 'HR Manager'),
        ('operations', 'Operations Specialist'),
        ('site_manager', 'Site Manager'),
        ('executive', 'Executive'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='viewer')
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    azure_ad_object_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    azure_ad_roles = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    @property
    def roles(self):
        """Return list of roles including Azure AD roles."""
        roles = [self.role] if self.role else []
        if self.azure_ad_roles:
            roles.extend(self.azure_ad_roles)
        return list(set(roles))
    
    def __str__(self):
        return self.username


class Account(models.Model):
    """
    Master entity for customers, vendors, and partners.
    This is the central entity bridging CRM and ERP functionality.
    """
    
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('partner', 'Partner'),
        ('prospect', 'Prospect'),
    ]
    
    TIER_CHOICES = [
        ('enterprise', 'Enterprise'),
        ('mid_market', 'Mid-Market'),
        ('smb', 'Small Business'),
        ('startup', 'Startup'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    PAYMENT_TERMS_CHOICES = [
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
        ('due_on_receipt', 'Due on Receipt'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='customer')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_accounts')
    account_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_accounts')
    
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='ZAR')
    
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    last_synced_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Contact(models.Model):
    """Individuals linked to accounts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    do_not_call = models.BooleanField(default=False)
    do_not_email = models.BooleanField(default=False)
    
    linkedin_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contacts'
        ordering = ['last_name', 'first_name']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.full_name


class Address(models.Model):
    """Physical addresses for accounts and contacts."""
    
    TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('physical', 'Physical'),
        ('mailing', 'Mailing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='physical')
    is_primary = models.BooleanField(default=False)
    
    street = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='South Africa')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'addresses'
    
    def __str__(self):
        return f"{self.street}, {self.city}"


class AuditLog(models.Model):
    """User activity tracking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} on {self.entity_type}"


class Favorite(models.Model):
    """User favorites for quick access."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    entity_title = models.CharField(max_length=255)
    entity_subtitle = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'entity_type', 'entity_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.entity_type}: {self.entity_title}"


class Event(models.Model):
    """Domain events for inter-service communication."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    retry_count = models.IntegerField(default=0)
    source_service = models.CharField(max_length=50, default='identity')
    correlation_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} ({self.status})"
