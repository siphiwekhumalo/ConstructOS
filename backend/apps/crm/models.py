import uuid
from django.db import models
from backend.apps.core.models import User


class Account(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    industry = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    type = models.TextField(default='customer')
    status = models.TextField(default='active')
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    employee_count = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'


class Contact(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone = models.TextField(null=True, blank=True)
    mobile = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    status = models.TextField(default='active')
    source = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'


class Address(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    street = models.TextField()
    city = models.TextField()
    state = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    country = models.TextField()
    type = models.TextField(default='billing')
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'addresses'


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
