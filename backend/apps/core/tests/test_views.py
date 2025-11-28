import pytest
import uuid
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from backend.apps.core.models import User, Event, AuditLog, Favorite


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_api_client(create_user):
    client = APIClient()
    user = create_user(role='admin', username=f'test_admin_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.mark.django_db
class TestAuthMeView:
    
    def test_auth_me_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUnifiedSearchView:
    
    def test_search_empty_query(self, api_client):
        response = api_client.get('/api/v1/search/', {'q': ''})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['contacts'] == []
        assert data['products'] == []
        assert data['orders'] == []
        assert data['tickets'] == []
        assert data['total'] == 0
    
    def test_search_short_query(self, api_client):
        response = api_client.get('/api/v1/search/', {'q': 'a'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['total'] == 0
    
    def test_search_with_results(self, api_client, create_contact, create_product):
        contact = create_contact(first_name='Johannes', last_name='Test')
        product = create_product(name='Construction Cement')
        
        response = api_client.get('/api/v1/search/', {'q': 'Johannes'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['contacts']) > 0
        assert data['contacts'][0]['title'] == 'Johannes Test'
    
    def test_search_products(self, api_client, create_product):
        product = create_product(name='Premium Steel Beams', sku='STEEL-001')
        
        response = api_client.get('/api/v1/search/', {'q': 'Steel'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['products']) > 0
        assert 'Steel' in data['products'][0]['title']


@pytest.mark.django_db
class TestUserViewSet:
    
    def test_list_users_authenticated(self, auth_api_client, create_user):
        user1 = create_user(username='user1')
        user2 = create_user(username='user2')
        
        response = auth_api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_user_authenticated(self, auth_api_client):
        user_data = {
            'username': f'newuser_{uuid.uuid4().hex[:8]}',
            'email': f'newuser_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'field_worker',
            'department': 'Operations',
        }
        response = auth_api_client.post('/api/v1/users/', user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert 'newuser_' in data['username']
    
    def test_get_user_detail_authenticated(self, auth_api_client, create_user):
        user = create_user(username=f'detailuser_{uuid.uuid4().hex[:8]}')
        
        response = auth_api_client.get(f'/api/v1/users/{user.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'detailuser_' in data['username']
    
    def test_update_user_authenticated(self, auth_api_client, create_user):
        user = create_user(username=f'updateuser_{uuid.uuid4().hex[:8]}')
        
        response = auth_api_client.patch(
            f'/api/v1/users/{user.id}/',
            {'first_name': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['first_name'] == 'Updated'
    
    def test_delete_user_authenticated(self, auth_api_client, create_user):
        user = create_user(username=f'deleteuser_{uuid.uuid4().hex[:8]}')
        
        response = auth_api_client.delete(f'/api/v1/users/{user.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert User.objects.filter(id=user.id).count() == 0


@pytest.mark.django_db
class TestEventViewSet:
    
    def test_list_events(self, api_client):
        Event.objects.create(
            id=str(uuid.uuid4()),
            type='test.event',
            payload='{}',
            source='test',
        )
        
        response = api_client.get('/api/v1/events/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_event(self, api_client):
        event_data = {
            'type': 'account.created',
            'payload': '{"id": "123"}',
            'source': 'crm',
        }
        response = api_client.post('/api/v1/events/', event_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestAuditLogViewSet:
    
    def test_list_audit_logs(self, api_client, create_user):
        user = create_user()
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            action='CREATE',
            entity_type='Account',
            entity_id=str(uuid.uuid4()),
        )
        
        response = api_client.get('/api/v1/audit-logs/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_cannot_create_audit_log_via_api(self, api_client):
        response = api_client.post('/api/v1/audit-logs/', {}, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestFavoriteViewSet:
    
    def test_list_favorites(self, api_client, create_user):
        user = create_user()
        Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='project',
            entity_id=str(uuid.uuid4()),
            entity_title='Test Project',
        )
        
        response = api_client.get('/api/v1/favorites/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_favorite(self, api_client, create_user):
        user = create_user()
        favorite_data = {
            'user': user.id,
            'entity_type': 'account',
            'entity_id': str(uuid.uuid4()),
            'entity_title': 'Favorite Account',
        }
        response = api_client.post('/api/v1/favorites/', favorite_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['entity_title'] == 'Favorite Account'
    
    def test_filter_favorites_by_user(self, api_client, create_user):
        user1 = create_user()
        user2 = create_user()
        
        Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user1,
            entity_type='project',
            entity_id=str(uuid.uuid4()),
            entity_title='User1 Project',
        )
        Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user2,
            entity_type='account',
            entity_id=str(uuid.uuid4()),
            entity_title='User2 Account',
        )
        
        response = api_client.get('/api/v1/favorites/', {'user_id': user1.id})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['entity_title'] == 'User1 Project'
    
    def test_delete_favorite(self, api_client, create_user):
        user = create_user()
        favorite = Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='contact',
            entity_id=str(uuid.uuid4()),
            entity_title='Test Contact',
        )
        
        response = api_client.delete(f'/api/v1/favorites/{favorite.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Favorite.objects.filter(id=favorite.id).count() == 0
