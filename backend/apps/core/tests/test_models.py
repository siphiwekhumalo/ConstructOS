import pytest
from decimal import Decimal
import uuid
from django.utils import timezone
from backend.apps.core.models import User, Event, AuditLog, Favorite


@pytest.mark.django_db
class TestUserModel:
    
    def test_create_user(self, user_data):
        user = User.objects.create(**user_data)
        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.role == user_data['role']
        assert user.is_active == True
    
    def test_user_str_representation(self, user_data):
        user = User.objects.create(**user_data)
        expected_str = f"{user.get_full_name()} ({user.get_role_display()})"
        assert str(user) == expected_str
    
    def test_user_roles_property(self, user_data):
        user_data['azure_ad_roles'] = ['Finance_User', 'Site_Manager']
        user = User.objects.create(**user_data)
        roles = user.roles
        assert 'user' in roles
        assert 'Finance_User' in roles
        assert 'Site_Manager' in roles
    
    def test_user_roles_empty_azure_ad(self, user_data):
        user = User.objects.create(**user_data)
        roles = user.roles
        assert roles == ['user']
    
    def test_user_has_role(self, user_data):
        user_data['role'] = 'admin'
        user_data['azure_ad_roles'] = ['Finance_User']
        user = User.objects.create(**user_data)
        assert user.has_role('admin') == True
        assert user.has_role('Finance_User') == True
        assert user.has_role('HR_Manager') == False
    
    def test_user_has_any_role(self, user_data):
        user_data['azure_ad_roles'] = ['Operations_Specialist']
        user = User.objects.create(**user_data)
        assert user.has_any_role(['Operations_Specialist', 'HR_Manager']) == True
        assert user.has_any_role(['HR_Manager', 'Finance_User']) == False
    
    def test_user_unique_username(self, user_data):
        User.objects.create(**user_data)
        user_data['id'] = str(uuid.uuid4())
        user_data['email'] = 'another@example.com'
        with pytest.raises(Exception):
            User.objects.create(**user_data)
    
    def test_user_unique_email(self, user_data):
        User.objects.create(**user_data)
        user_data['id'] = str(uuid.uuid4())
        user_data['username'] = 'anotheruser'
        with pytest.raises(Exception):
            User.objects.create(**user_data)
    
    def test_admin_user_role(self, admin_user_data):
        user = User.objects.create(**admin_user_data)
        assert user.role == 'admin'
        assert user.has_role('admin') == True
    
    def test_user_auto_timestamps(self, user_data):
        user = User.objects.create(**user_data)
        assert user.created_at is not None
        assert user.updated_at is not None


@pytest.mark.django_db
class TestEventModel:
    
    def test_create_event(self):
        event = Event.objects.create(
            id=str(uuid.uuid4()),
            type='account.created',
            payload='{"id": "123", "name": "Test"}',
            source='crm',
            status='pending',
        )
        assert event.type == 'account.created'
        assert event.status == 'pending'
        assert event.source == 'crm'
    
    def test_event_default_status(self):
        event = Event.objects.create(
            id=str(uuid.uuid4()),
            type='contact.updated',
            payload='{}',
            source='crm',
        )
        assert event.status == 'pending'
    
    def test_event_retry_count_default(self):
        event = Event.objects.create(
            id=str(uuid.uuid4()),
            type='contact.deleted',
            payload='{}',
            source='crm',
        )
        assert event.retry_count == 0
    
    def test_event_processed_at_nullable(self):
        event = Event.objects.create(
            id=str(uuid.uuid4()),
            type='test.event',
            payload='{}',
            source='test',
        )
        assert event.processed_at is None


@pytest.mark.django_db
class TestAuditLogModel:
    
    def test_create_audit_log(self, create_user):
        user = create_user()
        audit = AuditLog.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            action='CREATE',
            entity_type='Account',
            entity_id=str(uuid.uuid4()),
            new_values='{"name": "New Account"}',
        )
        assert audit.action == 'CREATE'
        assert audit.entity_type == 'Account'
        assert audit.user == user
    
    def test_audit_log_without_user(self):
        audit = AuditLog.objects.create(
            id=str(uuid.uuid4()),
            action='SYSTEM',
            entity_type='Settings',
            entity_id='global',
        )
        assert audit.user is None
    
    def test_audit_log_with_old_and_new_values(self, create_user):
        user = create_user()
        audit = AuditLog.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            action='UPDATE',
            entity_type='Project',
            entity_id=str(uuid.uuid4()),
            old_values='{"status": "active"}',
            new_values='{"status": "completed"}',
        )
        assert audit.old_values == '{"status": "active"}'
        assert audit.new_values == '{"status": "completed"}'


@pytest.mark.django_db
class TestFavoriteModel:
    
    def test_create_favorite(self, create_user):
        user = create_user()
        favorite = Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='project',
            entity_id=str(uuid.uuid4()),
            entity_title='Sandton Office Project',
        )
        assert favorite.entity_type == 'project'
        assert favorite.entity_title == 'Sandton Office Project'
        assert favorite.user == user
    
    def test_favorite_str_representation(self, create_user):
        user = create_user()
        favorite = Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='account',
            entity_id=str(uuid.uuid4()),
            entity_title='Test Company',
        )
        assert user.username in str(favorite)
        assert 'account' in str(favorite)
        assert 'Test Company' in str(favorite)
    
    def test_favorite_unique_constraint(self, create_user):
        user = create_user()
        entity_id = str(uuid.uuid4())
        Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='project',
            entity_id=entity_id,
            entity_title='Project A',
        )
        with pytest.raises(Exception):
            Favorite.objects.create(
                id=str(uuid.uuid4()),
                user=user,
                entity_type='project',
                entity_id=entity_id,
                entity_title='Project A Duplicate',
            )
    
    def test_favorite_with_subtitle(self, create_user):
        user = create_user()
        favorite = Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='contact',
            entity_id=str(uuid.uuid4()),
            entity_title='Thabo Molefe',
            entity_subtitle='Project Manager - Test Company',
        )
        assert favorite.entity_subtitle == 'Project Manager - Test Company'
    
    def test_cascade_delete_on_user(self, create_user):
        user = create_user()
        user_id = user.id
        Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='project',
            entity_id=str(uuid.uuid4()),
            entity_title='Test Project',
        )
        user.delete()
        assert Favorite.objects.filter(user_id=user_id).count() == 0
