import uuid
import json
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from backend.apps.core.models import User, Event


class Account(models.Model):
    """
    Master Account entity - the central bridge between CRM and ERP.
    This is the single source of truth for customer/vendor data.
    """
    ACCOUNT_TYPES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('partner', 'Partner'),
        ('prospect', 'Prospect'),
    ]
    
    PAYMENT_TERMS = [
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
        ('due_on_receipt', 'Due on Receipt'),
        ('custom', 'Custom'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    
    # Core identification
    account_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.TextField()
    legal_name = models.TextField(null=True, blank=True)
    
    # Classification
    industry = models.TextField(null=True, blank=True)
    type = models.TextField(default='customer', choices=ACCOUNT_TYPES)
    status = models.TextField(default='active')
    tier = models.TextField(null=True, blank=True)
    
    # Contact information
    website = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    fax = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    
    # Financial/ERP integration fields
    tax_id = models.CharField(max_length=100, null=True, blank=True)
    vat_number = models.CharField(max_length=100, null=True, blank=True)
    payment_terms = models.TextField(default='net_30', choices=PAYMENT_TERMS)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Business metrics
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    employee_count = models.IntegerField(null=True, blank=True)
    
    # Hierarchy
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_accounts')
    
    # Ownership and management
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id', related_name='owned_accounts')
    account_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_accounts')
    
    # Additional info
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    
    # Sync tracking for microservices
    last_synced_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        
    def __str__(self):
        return self.name
    
    def get_primary_billing_address(self):
        return self.address_set.filter(type='billing', is_primary=True).first()
    
    def get_primary_shipping_address(self):
        return self.address_set.filter(type='shipping', is_primary=True).first()
    
    def get_primary_contact(self):
        return self.contact_set.filter(is_primary=True).first()


class Contact(models.Model):
    """
    Contact entity linked to Accounts.
    Represents individuals who interact with the business.
    """
    COMMUNICATION_PREFERENCES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('mail', 'Mail'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    
    # Personal information
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone = models.TextField(null=True, blank=True)
    mobile = models.TextField(null=True, blank=True)
    
    # Professional information
    title = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    
    # Account relationship
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    is_primary = models.BooleanField(default=False)
    
    # Communication preferences
    preferred_communication = models.TextField(default='email', choices=COMMUNICATION_PREFERENCES)
    do_not_contact = models.BooleanField(default=False)
    email_opt_out = models.BooleanField(default=False)
    
    # Social profiles
    linkedin_url = models.TextField(null=True, blank=True)
    twitter_handle = models.TextField(null=True, blank=True)
    
    # CRM fields
    status = models.TextField(default='active')
    source = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    
    # Sync tracking
    last_synced_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    """
    Address entity for both Accounts and Contacts.
    Supports billing, shipping, and other address types.
    """
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('mailing', 'Mailing'),
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    
    # Address details
    street = models.TextField()
    street2 = models.TextField(null=True, blank=True)
    city = models.TextField()
    state = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    country = models.TextField()
    
    # Classification
    type = models.TextField(default='billing', choices=ADDRESS_TYPES)
    is_primary = models.BooleanField(default=False)
    
    # Relationships
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    
    # Validation
    is_validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'addresses'
        
    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"


class PipelineStage(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    order = models.IntegerField()
    probability = models.IntegerField(default=0)
    color = models.TextField(default='#3B82F6')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pipeline_stages'


class Lead(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone = models.TextField(null=True, blank=True)
    company = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    status = models.TextField(default='new')
    rating = models.TextField(null=True, blank=True)
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    converted_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='converted_contact_id')
    converted_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='converted_account_id', related_name='converted_leads')
    converted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'


class Opportunity(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True, db_column='stage_id')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    probability = models.IntegerField(default=0)
    close_date = models.DateTimeField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.TextField(default='open')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'opportunities'


class Campaign(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    type = models.TextField()
    status = models.TextField(default='draft')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    target_audience = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'


class MailingList(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    member_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mailing_lists'


class Segment(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    criteria = models.TextField(null=True, blank=True)
    member_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'segments'


class Sla(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    response_time_hours = models.IntegerField()
    resolution_time_hours = models.IntegerField()
    priority = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'slas'


class Ticket(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    ticket_number = models.TextField(unique=True)
    subject = models.TextField()
    description = models.TextField(null=True, blank=True)
    status = models.TextField(default='open')
    priority = models.TextField(default='medium')
    type = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='assigned_to_id')
    sla = models.ForeignKey(Sla, on_delete=models.SET_NULL, null=True, db_column='sla_id')
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'


class TicketComment(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_column='ticket_id')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='author_id')
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_comments'


class Client(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    company = models.TextField()
    role = models.TextField()
    email = models.TextField()
    phone = models.TextField()
    status = models.TextField()
    avatar = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'


# ============================================================================
# DOMAIN EVENTS - For CRM-ERP sync and microservices integration
# ============================================================================

def create_domain_event(event_type: str, entity_type: str, entity_id: str, payload: dict, source: str = 'crm'):
    """
    Helper function to create domain events for cross-service synchronization.
    """
    Event.objects.create(
        type=event_type,
        payload=json.dumps({
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'data': payload,
        }),
        source=source,
        status='pending'
    )


@receiver(post_save, sender=Account)
def account_saved(sender, instance, created, **kwargs):
    """Emit event when account is created or updated."""
    event_type = 'account.created' if created else 'account.updated'
    payload = {
        'id': str(instance.id),
        'account_number': instance.account_number,
        'name': instance.name,
        'type': instance.type,
        'status': instance.status,
        'email': instance.email,
        'phone': instance.phone,
        'tax_id': instance.tax_id,
        'payment_terms': instance.payment_terms,
        'credit_limit': str(instance.credit_limit) if instance.credit_limit else None,
        'currency': instance.currency,
    }
    create_domain_event(event_type, 'Account', instance.id, payload)


@receiver(post_delete, sender=Account)
def account_deleted(sender, instance, **kwargs):
    """Emit event when account is deleted."""
    payload = {
        'id': str(instance.id),
        'name': instance.name,
    }
    create_domain_event('account.deleted', 'Account', instance.id, payload)


@receiver(post_save, sender=Contact)
def contact_saved(sender, instance, created, **kwargs):
    """Emit event when contact is created or updated."""
    event_type = 'contact.created' if created else 'contact.updated'
    payload = {
        'id': str(instance.id),
        'first_name': instance.first_name,
        'last_name': instance.last_name,
        'email': instance.email,
        'phone': instance.phone,
        'account_id': str(instance.account_id) if instance.account_id else None,
        'is_primary': instance.is_primary,
    }
    create_domain_event(event_type, 'Contact', instance.id, payload)


@receiver(post_delete, sender=Contact)
def contact_deleted(sender, instance, **kwargs):
    """Emit event when contact is deleted."""
    payload = {
        'id': str(instance.id),
        'email': instance.email,
        'account_id': str(instance.account_id) if instance.account_id else None,
    }
    create_domain_event('contact.deleted', 'Contact', instance.id, payload)
