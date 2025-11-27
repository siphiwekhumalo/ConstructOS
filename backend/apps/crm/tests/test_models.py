import pytest
from decimal import Decimal
import uuid
from django.utils import timezone
from backend.apps.crm.models import (
    Account, Contact, Address, Lead, Opportunity, 
    Campaign, Ticket, Sla, Client, PipelineStage
)


@pytest.mark.django_db
class TestAccountModel:
    
    def test_create_account(self, account_data):
        account = Account.objects.create(**account_data)
        assert account.name == account_data['name']
        assert account.type == 'customer'
        assert account.currency == 'ZAR'
    
    def test_account_str_representation(self, account_data):
        account = Account.objects.create(**account_data)
        assert str(account) == account_data['name']
    
    def test_account_payment_terms(self, account_data):
        account_data['payment_terms'] = 'net_45'
        account = Account.objects.create(**account_data)
        assert account.payment_terms == 'net_45'
    
    def test_account_credit_limit(self, account_data):
        account = Account.objects.create(**account_data)
        assert account.credit_limit == Decimal('500000.00')
    
    def test_account_unique_account_number(self, account_data):
        Account.objects.create(**account_data)
        account_data['id'] = str(uuid.uuid4())
        account_data['name'] = 'Another Company'
        with pytest.raises(Exception):
            Account.objects.create(**account_data)
    
    def test_account_default_type(self):
        account = Account.objects.create(
            id=str(uuid.uuid4()),
            name='Test Company',
        )
        assert account.type == 'customer'
    
    def test_account_default_payment_terms(self):
        account = Account.objects.create(
            id=str(uuid.uuid4()),
            name='Test Company',
        )
        assert account.payment_terms == 'net_30'
    
    def test_account_timestamps(self, account_data):
        account = Account.objects.create(**account_data)
        assert account.created_at is not None
        assert account.updated_at is not None
    
    def test_get_primary_billing_address(self, account_data):
        account = Account.objects.create(**account_data)
        Address.objects.create(
            id=str(uuid.uuid4()),
            street='123 Main Street',
            city='Johannesburg',
            country='South Africa',
            type='billing',
            is_primary=True,
            account=account,
        )
        primary = account.get_primary_billing_address()
        assert primary is not None
        assert primary.city == 'Johannesburg'
    
    def test_get_primary_shipping_address(self, account_data):
        account = Account.objects.create(**account_data)
        Address.objects.create(
            id=str(uuid.uuid4()),
            street='456 Industrial Road',
            city='Cape Town',
            country='South Africa',
            type='shipping',
            is_primary=True,
            account=account,
        )
        primary = account.get_primary_shipping_address()
        assert primary is not None
        assert primary.city == 'Cape Town'
    
    def test_get_primary_contact(self, account_data, contact_data):
        account = Account.objects.create(**account_data)
        contact_data['account'] = account
        Contact.objects.create(**contact_data)
        primary = account.get_primary_contact()
        assert primary is not None
        assert primary.is_primary == True


@pytest.mark.django_db
class TestContactModel:
    
    def test_create_contact(self, contact_data, create_account):
        account = create_account()
        contact_data['account'] = account
        contact = Contact.objects.create(**contact_data)
        assert contact.first_name == contact_data['first_name']
        assert contact.email == contact_data['email']
        assert contact.is_primary == True
    
    def test_contact_str_representation(self, contact_data, create_account):
        account = create_account()
        contact_data['account'] = account
        contact = Contact.objects.create(**contact_data)
        assert str(contact) == f"{contact_data['first_name']} {contact_data['last_name']}"
    
    def test_contact_full_name_property(self, contact_data, create_account):
        account = create_account()
        contact_data['account'] = account
        contact = Contact.objects.create(**contact_data)
        assert contact.full_name == 'Thabo Molefe'
    
    def test_contact_preferred_communication_default(self, create_account):
        account = create_account()
        contact = Contact.objects.create(
            id=str(uuid.uuid4()),
            first_name='Test',
            last_name='Contact',
            email='test@example.com',
            account=account,
        )
        assert contact.preferred_communication == 'email'
    
    def test_contact_opt_out_flags(self, contact_data, create_account):
        account = create_account()
        contact_data['account'] = account
        contact_data['do_not_contact'] = True
        contact_data['email_opt_out'] = True
        contact = Contact.objects.create(**contact_data)
        assert contact.do_not_contact == True
        assert contact.email_opt_out == True


@pytest.mark.django_db
class TestAddressModel:
    
    def test_create_billing_address(self, create_account):
        account = create_account()
        address = Address.objects.create(
            id=str(uuid.uuid4()),
            street='100 Nelson Mandela Square',
            city='Sandton',
            state='Gauteng',
            postal_code='2196',
            country='South Africa',
            type='billing',
            is_primary=True,
            account=account,
        )
        assert address.type == 'billing'
        assert address.city == 'Sandton'
    
    def test_address_str_representation(self, create_account):
        account = create_account()
        address = Address.objects.create(
            id=str(uuid.uuid4()),
            street='50 Long Street',
            city='Cape Town',
            country='South Africa',
            type='mailing',
            account=account,
        )
        assert 'Long Street' in str(address)
        assert 'Cape Town' in str(address)
    
    def test_address_validation_flags(self, create_account):
        account = create_account()
        address = Address.objects.create(
            id=str(uuid.uuid4()),
            street='100 Main Road',
            city='Durban',
            country='South Africa',
            type='shipping',
            is_validated=True,
            validated_at=timezone.now(),
            account=account,
        )
        assert address.is_validated == True
        assert address.validated_at is not None


@pytest.mark.django_db
class TestLeadModel:
    
    def test_create_lead(self, lead_data):
        lead = Lead.objects.create(**lead_data)
        assert lead.first_name == lead_data['first_name']
        assert lead.status == 'new'
        assert lead.rating == 'hot'
    
    def test_lead_estimated_value(self, lead_data):
        lead = Lead.objects.create(**lead_data)
        assert lead.estimated_value == Decimal('5000000.00')
    
    def test_lead_default_status(self):
        lead = Lead.objects.create(
            id=str(uuid.uuid4()),
            first_name='Test',
            last_name='Lead',
            email='test.lead@example.com',
        )
        assert lead.status == 'new'
    
    def test_lead_conversion(self, lead_data, create_account, create_contact):
        lead = Lead.objects.create(**lead_data)
        account = create_account()
        contact = create_contact(account=account)
        lead.converted_account = account
        lead.converted_contact = contact
        lead.converted_at = timezone.now()
        lead.status = 'converted'
        lead.save()
        lead.refresh_from_db()
        assert lead.converted_account == account
        assert lead.converted_contact == contact
        assert lead.status == 'converted'


@pytest.mark.django_db
class TestOpportunityModel:
    
    def test_create_opportunity(self, opportunity_data, create_account):
        account = create_account()
        opportunity_data['account'] = account
        opportunity = Opportunity.objects.create(**opportunity_data)
        assert opportunity.name == opportunity_data['name']
        assert opportunity.amount == Decimal('25000000.00')
        assert opportunity.probability == 60
    
    def test_opportunity_default_status(self, create_account):
        account = create_account()
        opportunity = Opportunity.objects.create(
            id=str(uuid.uuid4()),
            name='Test Opportunity',
            amount=Decimal('1000000.00'),
            account=account,
        )
        assert opportunity.status == 'open'
    
    def test_opportunity_with_stage(self, opportunity_data, create_account):
        account = create_account()
        stage = PipelineStage.objects.create(
            id=str(uuid.uuid4()),
            name='Proposal',
            order=2,
            probability=40,
            color='#10B981',
        )
        opportunity_data['account'] = account
        opportunity_data['stage'] = stage
        opportunity = Opportunity.objects.create(**opportunity_data)
        assert opportunity.stage.name == 'Proposal'


@pytest.mark.django_db
class TestCampaignModel:
    
    def test_create_campaign(self, campaign_data):
        campaign = Campaign.objects.create(**campaign_data)
        assert campaign.name == campaign_data['name']
        assert campaign.type == 'trade_show'
        assert campaign.budget == Decimal('150000.00')
    
    def test_campaign_default_status(self):
        campaign = Campaign.objects.create(
            id=str(uuid.uuid4()),
            name='Test Campaign',
            type='email',
        )
        assert campaign.status == 'draft'
    
    def test_campaign_date_range(self, campaign_data):
        campaign = Campaign.objects.create(**campaign_data)
        assert campaign.start_date <= campaign.end_date


@pytest.mark.django_db
class TestTicketModel:
    
    def test_create_ticket(self, ticket_data, create_account):
        account = create_account()
        ticket_data['account'] = account
        ticket = Ticket.objects.create(**ticket_data)
        assert ticket.ticket_number == ticket_data['ticket_number']
        assert ticket.status == 'open'
        assert ticket.priority == 'medium'
    
    def test_ticket_unique_number(self, ticket_data):
        Ticket.objects.create(**ticket_data)
        ticket_data['id'] = str(uuid.uuid4())
        ticket_data['subject'] = 'Another Ticket'
        with pytest.raises(Exception):
            Ticket.objects.create(**ticket_data)
    
    def test_ticket_with_sla(self, ticket_data, sla_data, create_account):
        account = create_account()
        sla = Sla.objects.create(**sla_data)
        ticket_data['account'] = account
        ticket_data['sla'] = sla
        ticket = Ticket.objects.create(**ticket_data)
        assert ticket.sla.name == 'Premium Support SLA'
        assert ticket.sla.response_time_hours == 4
    
    def test_ticket_resolution(self, ticket_data, create_account):
        account = create_account()
        ticket_data['account'] = account
        ticket = Ticket.objects.create(**ticket_data)
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.save()
        ticket.refresh_from_db()
        assert ticket.status == 'resolved'
        assert ticket.resolved_at is not None


@pytest.mark.django_db
class TestSlaModel:
    
    def test_create_sla(self, sla_data):
        sla = Sla.objects.create(**sla_data)
        assert sla.name == sla_data['name']
        assert sla.response_time_hours == 4
        assert sla.resolution_time_hours == 24
        assert sla.is_active == True
    
    def test_sla_priority_levels(self):
        sla_high = Sla.objects.create(
            id=str(uuid.uuid4()),
            name='Critical SLA',
            response_time_hours=1,
            resolution_time_hours=4,
            priority='critical',
        )
        sla_low = Sla.objects.create(
            id=str(uuid.uuid4()),
            name='Standard SLA',
            response_time_hours=24,
            resolution_time_hours=72,
            priority='low',
        )
        assert sla_high.response_time_hours < sla_low.response_time_hours


@pytest.mark.django_db
class TestClientModel:
    
    def test_create_client(self, create_account):
        account = create_account()
        client = Client.objects.create(
            id=str(uuid.uuid4()),
            name='Sipho Dlamini',
            company='Dlamini Developments',
            role='Director',
            email='sipho@dlamini.co.za',
            phone='+27 82 555 1234',
            status='active',
            avatar='https://example.com/avatar.jpg',
            account=account,
        )
        assert client.name == 'Sipho Dlamini'
        assert client.account == account
    
    def test_client_timestamps(self, create_account):
        account = create_account()
        client = Client.objects.create(
            id=str(uuid.uuid4()),
            name='Test Client',
            company='Test Co',
            role='Manager',
            email='test@example.com',
            phone='+27 11 111 1111',
            status='active',
            avatar='',
            account=account,
        )
        assert client.created_at is not None
        assert client.updated_at is not None
