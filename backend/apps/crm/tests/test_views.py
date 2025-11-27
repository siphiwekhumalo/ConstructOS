import pytest
import uuid
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from backend.apps.crm.models import (
    Account, Contact, Address, Lead, Opportunity, 
    Campaign, Ticket, Sla, Client
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAccountViewSet:
    
    def test_list_accounts(self, api_client, create_account):
        account1 = create_account(name='Company One')
        account2 = create_account(name='Company Two')
        
        response = api_client.get('/api/v1/accounts/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_account(self, api_client):
        account_data = {
            'name': 'New Construction Company',
            'type': 'customer',
            'industry': 'Construction',
            'email': 'info@newconstruction.co.za',
            'phone': '+27 11 555 1234',
            'currency': 'ZAR',
        }
        response = api_client.post('/api/v1/accounts/', account_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'New Construction Company'
        assert data['currency'] == 'ZAR'
    
    def test_get_account_detail(self, api_client, create_account):
        account = create_account(name='Detail Company')
        
        response = api_client.get(f'/api/v1/accounts/{account.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Detail Company'
    
    def test_update_account(self, api_client, create_account):
        account = create_account(name='Old Name')
        
        response = api_client.patch(
            f'/api/v1/accounts/{account.id}/',
            {'name': 'Updated Name'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Updated Name'
    
    def test_delete_account(self, api_client, create_account):
        account = create_account()
        
        response = api_client.delete(f'/api/v1/accounts/{account.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Account.objects.filter(id=account.id).count() == 0
    
    def test_filter_accounts_by_status(self, api_client, create_account):
        active_account = create_account(status='active')
        inactive_account = create_account(status='inactive')
        
        response = api_client.get('/api/v1/accounts/', {'status': 'active'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for account in data['results']:
            assert account['status'] == 'active'
    
    def test_filter_accounts_by_type(self, api_client, create_account):
        customer = create_account(type='customer')
        vendor = create_account(type='vendor')
        
        response = api_client.get('/api/v1/accounts/', {'type': 'vendor'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for account in data['results']:
            assert account['type'] == 'vendor'
    
    def test_account_lookup(self, api_client, create_account):
        account = create_account(name='Searchable Company')
        
        response = api_client.get('/api/v1/accounts/lookup/', {'term': 'Search'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert 'Searchable' in data[0]['name']
    
    def test_account_lookup_short_term(self, api_client):
        response = api_client.get('/api/v1/accounts/lookup/', {'term': 'a'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    def test_account_related_data(self, api_client, create_account, create_contact):
        account = create_account()
        contact = create_contact(account=account)
        
        response = api_client.get(f'/api/v1/accounts/{account.id}/related/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'open_tickets' in data
        assert 'recent_invoices' in data
        assert 'contacts' in data


@pytest.mark.django_db
class TestContactViewSet:
    
    def test_list_contacts(self, api_client, create_contact):
        contact1 = create_contact(first_name='John')
        contact2 = create_contact(first_name='Jane')
        
        response = api_client.get('/api/v1/contacts/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_contact(self, api_client, create_account):
        account = create_account()
        contact_data = {
            'first_name': 'Thabo',
            'last_name': 'Nkosi',
            'email': 'thabo@example.co.za',
            'phone': '+27 82 555 1234',
            'title': 'Site Manager',
            'account': account.id,
        }
        response = api_client.post('/api/v1/contacts/', contact_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['first_name'] == 'Thabo'
    
    def test_get_contact_detail(self, api_client, create_contact):
        contact = create_contact(first_name='Detail', last_name='Contact')
        
        response = api_client.get(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['first_name'] == 'Detail'
    
    def test_filter_contacts_by_account(self, api_client, create_account, create_contact):
        account1 = create_account()
        account2 = create_account()
        contact1 = create_contact(account=account1)
        contact2 = create_contact(account=account2)
        
        response = api_client.get('/api/v1/contacts/', {'account': account1.id})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for contact in data['results']:
            assert contact['account'] == account1.id


@pytest.mark.django_db
class TestLeadViewSet:
    
    def test_list_leads(self, api_client, lead_data):
        Lead.objects.create(**lead_data)
        
        response = api_client.get('/api/v1/leads/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_lead(self, api_client):
        lead_data = {
            'first_name': 'New',
            'last_name': 'Lead',
            'email': 'new.lead@example.com',
            'company': 'Prospect Co',
            'source': 'website',
        }
        response = api_client.post('/api/v1/leads/', lead_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['first_name'] == 'New'
    
    def test_convert_lead(self, api_client, lead_data):
        lead = Lead.objects.create(**lead_data)
        
        response = api_client.post(f'/api/v1/leads/{lead.id}/convert/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'account_id' in data
        assert 'contact_id' in data
        
        lead.refresh_from_db()
        assert lead.status == 'converted'
        assert lead.converted_account is not None
        assert lead.converted_contact is not None


@pytest.mark.django_db
class TestOpportunityViewSet:
    
    def test_list_opportunities(self, api_client, create_account, opportunity_data):
        account = create_account()
        opportunity_data['account'] = account
        Opportunity.objects.create(**opportunity_data)
        
        response = api_client.get('/api/v1/opportunities/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_opportunity(self, api_client, create_account):
        account = create_account()
        opp_data = {
            'name': 'New Project Opportunity',
            'account': account.id,
            'amount': '5000000.00',
            'probability': 50,
            'status': 'open',
        }
        response = api_client.post('/api/v1/opportunities/', opp_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'New Project Opportunity'


@pytest.mark.django_db
class TestTicketViewSet:
    
    def test_list_tickets(self, api_client, ticket_data, create_account):
        account = create_account()
        ticket_data['account'] = account
        Ticket.objects.create(**ticket_data)
        
        response = api_client.get('/api/v1/tickets/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_ticket(self, api_client, create_account):
        account = create_account()
        ticket_data = {
            'subject': 'Equipment Issue',
            'description': 'Excavator not starting',
            'priority': 'high',
            'type': 'technical',
            'account': account.id,
        }
        response = api_client.post('/api/v1/tickets/', ticket_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['subject'] == 'Equipment Issue'
        assert 'ticket_number' in data
        assert data['ticket_number'].startswith('TKT-')
    
    def test_filter_tickets_by_priority(self, api_client, create_account):
        account = create_account()
        Ticket.objects.create(
            id=str(uuid.uuid4()),
            ticket_number='TKT-HIGH-001',
            subject='High Priority',
            priority='high',
            account=account,
        )
        Ticket.objects.create(
            id=str(uuid.uuid4()),
            ticket_number='TKT-LOW-001',
            subject='Low Priority',
            priority='low',
            account=account,
        )
        
        response = api_client.get('/api/v1/tickets/', {'priority': 'high'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for ticket in data['results']:
            assert ticket['priority'] == 'high'


@pytest.mark.django_db
class TestCampaignViewSet:
    
    def test_list_campaigns(self, api_client, campaign_data):
        Campaign.objects.create(**campaign_data)
        
        response = api_client.get('/api/v1/campaigns/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_campaign(self, api_client):
        campaign_data = {
            'name': 'Q2 Marketing Push',
            'type': 'email',
            'status': 'draft',
            'budget': '100000.00',
        }
        response = api_client.post('/api/v1/campaigns/', campaign_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'Q2 Marketing Push'


@pytest.mark.django_db
class TestSlaViewSet:
    
    def test_list_slas(self, api_client, sla_data):
        Sla.objects.create(**sla_data)
        
        response = api_client.get('/api/v1/slas/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_sla(self, api_client):
        sla_data = {
            'name': 'Standard Support',
            'response_time_hours': 8,
            'resolution_time_hours': 48,
            'priority': 'medium',
        }
        response = api_client.post('/api/v1/slas/', sla_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'Standard Support'


@pytest.mark.django_db
class TestClientViewSet:
    
    def test_list_clients(self, api_client, create_account):
        account = create_account()
        Client.objects.create(
            id=str(uuid.uuid4()),
            name='Test Client',
            company='Test Company',
            role='Director',
            email='test@example.com',
            phone='+27 11 111 1111',
            status='active',
            avatar='https://example.com/avatar.jpg',
            account=account,
        )
        
        response = api_client.get('/api/v1/clients/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_client(self, api_client, create_account):
        account = create_account()
        client_data = {
            'name': 'New Client',
            'company': 'Client Company',
            'role': 'CEO',
            'email': 'client@example.com',
            'phone': '+27 82 555 9999',
            'status': 'active',
            'avatar': 'https://example.com/new-avatar.jpg',
            'account': account.id,
        }
        response = api_client.post('/api/v1/clients/', client_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'New Client'
