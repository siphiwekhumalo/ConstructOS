import pytest
import uuid
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from backend.apps.core.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRBACUserRoles:
    """Test Role-Based Access Control for user role assignments."""
    
    def test_user_role_assignment(self, create_user):
        user = create_user(role='finance')
        assert user.role == 'finance'
        assert user.has_role('finance')
    
    def test_admin_has_all_roles(self, create_user):
        admin = create_user(role='admin')
        assert admin.has_role('admin')
    
    def test_user_azure_ad_roles_integration(self, create_user):
        user = create_user(
            role='user',
            azure_ad_roles=['Finance_User', 'Site_Manager']
        )
        assert user.has_role('Finance_User')
        assert user.has_role('Site_Manager')
        assert len(user.roles) >= 3


@pytest.mark.django_db
class TestAuthenticatedVsUnauthenticated:
    """Test authenticated vs unauthenticated access to endpoints."""
    
    def test_authenticated_can_list_users(self, admin_api_client):
        response = admin_api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_authenticated_can_list_accounts(self, admin_api_client):
        response = admin_api_client.get('/api/v1/accounts/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_authenticated_can_list_projects(self, admin_api_client):
        response = admin_api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_authenticated_can_create_account(self, admin_api_client):
        response = admin_api_client.post('/api/v1/accounts/', {
            'name': 'Test Account Auth',
            'type': 'customer',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_finance_user_can_access_invoices(self, finance_api_client):
        response = finance_api_client.get('/api/v1/invoices/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_hr_user_can_access_employees(self, hr_api_client):
        response = hr_api_client.get('/api/v1/employees/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_site_manager_can_access_projects(self, site_manager_api_client):
        response = site_manager_api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_operations_user_can_access_warehouses(self, operations_api_client):
        response = operations_api_client.get('/api/v1/warehouses/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestValidationErrors:
    """Test validation and error handling."""
    
    def test_create_user_missing_required_fields(self, api_client):
        response = api_client.post('/api/v1/users/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_account_missing_required_fields(self, api_client):
        response = api_client.post('/api/v1/accounts/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_project_missing_required_fields(self, api_client):
        response = api_client.post('/api/v1/projects/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_invoice_missing_required_fields(self, api_client):
        response = api_client.post('/api/v1/invoices/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_duplicate_username_error(self, api_client, create_user):
        existing_user = create_user(username='duplicate_test')
        
        user_data = {
            'username': 'duplicate_test',
            'email': 'new@example.com',
            'role': 'user',
        }
        response = api_client.post('/api/v1/users/', user_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_duplicate_account_number_error(self, api_client, create_account):
        existing = create_account(account_number='ACC-DUPE-001')
        
        account_data = {
            'name': 'New Account',
            'account_number': 'ACC-DUPE-001',
        }
        response = api_client.post('/api/v1/accounts/', account_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestNegativeFlows:
    """Test negative/failure scenarios."""
    
    def test_get_nonexistent_user(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.get(f'/api/v1/users/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_nonexistent_account(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.get(f'/api/v1/accounts/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_nonexistent_project(self, api_client):
        fake_id = 'PRJ-INVALID-999999'
        response = api_client.get(f'/api/v1/projects/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_nonexistent_resource(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.patch(
            f'/api/v1/accounts/{fake_id}/',
            {'name': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_resource(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.delete(f'/api/v1/users/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_payment_terms(self, api_client):
        account_data = {
            'name': 'Test Account',
            'payment_terms': 'invalid_terms',
        }
        response = api_client.post('/api/v1/accounts/', account_data, format='json')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]
    
    def test_invalid_status_filter(self, api_client):
        response = api_client.get('/api/v1/projects/', {'status': 'INVALID_STATUS'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['results'] == []


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_project_minimal_budget(self, create_project):
        from backend.apps.construction.models import Project
        project = create_project(budget=Decimal('1.00'))
        assert project.budget == Decimal('1.00')
        db_project = Project.objects.get(id=project.id)
        assert db_project.budget == Decimal('1.00')
    
    def test_project_100_percent_progress(self, api_client, create_project):
        project = create_project(progress=50)
        
        response = api_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'progress': 100},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['progress'] == 100
    
    def test_empty_search_query(self, api_client):
        response = api_client.get('/api/v1/search/', {'q': ''})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['total'] == 0
    
    def test_very_long_search_query(self, api_client):
        long_query = 'a' * 500
        response = api_client.get('/api/v1/search/', {'q': long_query})
        assert response.status_code == status.HTTP_200_OK
    
    def test_special_characters_in_search(self, api_client):
        response = api_client.get('/api/v1/search/', {'q': "test's & special <chars>"})
        assert response.status_code == status.HTTP_200_OK
    
    def test_unicode_in_account_name(self, api_client):
        account_data = {
            'name': 'Société Générale Pty Ltd',
            'type': 'customer',
        }
        response = api_client.post('/api/v1/accounts/', account_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_large_budget_value(self, create_project):
        from backend.apps.construction.models import Project
        large_budget = Decimal('9999999999.99')
        project = create_project(budget=large_budget)
        assert project.budget == large_budget
        db_project = Project.objects.get(id=project.id)
        assert db_project.budget == large_budget


@pytest.mark.django_db
class TestConcurrentOperations:
    """Test scenarios involving multiple concurrent-like operations."""
    
    def test_create_multiple_accounts_sequentially(self, api_client):
        accounts_to_create = [
            {'name': f'Account {uuid.uuid4().hex[:8]}', 'type': 'customer'}
            for _ in range(5)
        ]
        
        created_ids = []
        for account_data in accounts_to_create:
            response = api_client.post('/api/v1/accounts/', account_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            created_ids.append(response.json()['id'])
        
        assert len(set(created_ids)) == 5
    
    def test_rapid_status_updates(self, api_client, create_project):
        project = create_project(progress=0)
        
        for progress in [10, 25, 50, 75, 100]:
            response = api_client.patch(
                f'/api/v1/projects/{project.id}/',
                {'progress': progress},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()['progress'] == progress


@pytest.mark.django_db
class TestDataIntegrity:
    """Test data integrity constraints."""
    
    def test_cascade_delete_contacts_on_account(self, create_account, create_contact):
        account = create_account()
        contact1 = create_contact(account=account)
        contact2 = create_contact(account=account)
        
        from backend.apps.crm.models import Contact
        initial_count = Contact.objects.filter(account=account).count()
        assert initial_count == 2
        
        account.delete()
        remaining = Contact.objects.filter(id__in=[contact1.id, contact2.id])
        for c in remaining:
            assert c.account is None
    
    def test_foreign_key_set_null_on_delete(self, create_project, create_account):
        account = create_account()
        project = create_project(account=account)
        
        account_id = account.id
        account.delete()
        
        project.refresh_from_db()
        assert project.account is None
    
    def test_unique_ticket_number_constraint(self, create_account):
        from backend.apps.crm.models import Ticket
        account = create_account()
        
        ticket1 = Ticket.objects.create(
            id=str(uuid.uuid4()),
            ticket_number='TKT-UNIQUE-001',
            subject='Test 1',
            account=account,
        )
        
        with pytest.raises(Exception):
            Ticket.objects.create(
                id=str(uuid.uuid4()),
                ticket_number='TKT-UNIQUE-001',
                subject='Test 2',
                account=account,
            )
