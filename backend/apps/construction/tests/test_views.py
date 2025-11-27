import pytest
import uuid
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from backend.apps.construction.models import (
    Project, Transaction, Equipment, SafetyInspection, Document
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestProjectViewSet:
    
    def test_list_projects(self, api_client, create_project):
        project1 = create_project(name='Project Alpha')
        project2 = create_project(name='Project Beta')
        
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_project(self, api_client, create_account):
        account = create_account()
        project_data = {
            'name': 'New Office Building',
            'location': 'Sandton, Johannesburg',
            'status': 'planning',
            'budget': '25000000.00',
            'due_date': '2025-12-31',
            'progress': 0,
            'account': account.id,
        }
        response = api_client.post('/api/v1/projects/', project_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'New Office Building'
        assert data['id'].startswith('PRJ-')
    
    def test_get_project_detail(self, api_client, create_project):
        project = create_project(name='Detail Project')
        
        response = api_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Detail Project'
    
    def test_update_project_progress(self, api_client, create_project):
        project = create_project(progress=25)
        
        response = api_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'progress': 50},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['progress'] == 50
    
    def test_update_project_status(self, api_client, create_project):
        project = create_project(status='active')
        
        response = api_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'status': 'completed'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'completed'
    
    def test_delete_project(self, api_client, create_project):
        project = create_project()
        
        response = api_client.delete(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Project.objects.filter(id=project.id).count() == 0
    
    def test_filter_projects_by_status(self, api_client, create_project):
        active = create_project(status='active')
        completed = create_project(status='completed')
        
        response = api_client.get('/api/v1/projects/', {'status': 'active'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for project in data['results']:
            assert project['status'] == 'active'
    
    def test_search_projects_by_name(self, api_client, create_project):
        project = create_project(name='Sandton Tower')
        
        response = api_client.get('/api/v1/projects/', {'search': 'Sandton'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['results']) > 0


@pytest.mark.django_db
class TestTransactionViewSet:
    
    def test_list_transactions(self, api_client, create_project):
        project = create_project()
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Material purchase',
            amount=Decimal('100000.00'),
            status='completed',
            type='expense',
        )
        
        response = api_client.get('/api/v1/transactions/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_transaction(self, api_client, create_project):
        project = create_project()
        transaction_data = {
            'project': project.id,
            'description': 'Steel purchase',
            'amount': '250000.00',
            'status': 'pending',
            'type': 'expense',
            'category': 'materials',
        }
        response = api_client.post('/api/v1/transactions/', transaction_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['description'] == 'Steel purchase'
    
    def test_filter_transactions_by_type(self, api_client, create_project):
        project = create_project()
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Expense',
            amount=Decimal('50000.00'),
            status='completed',
            type='expense',
        )
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Income',
            amount=Decimal('500000.00'),
            status='completed',
            type='income',
        )
        
        response = api_client.get('/api/v1/transactions/', {'type': 'income'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for transaction in data['results']:
            assert transaction['type'] == 'income'
    
    def test_filter_transactions_by_project(self, api_client, create_project):
        project1 = create_project()
        project2 = create_project()
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project1,
            description='Project 1 expense',
            amount=Decimal('10000.00'),
            status='completed',
        )
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project2,
            description='Project 2 expense',
            amount=Decimal('20000.00'),
            status='completed',
        )
        
        response = api_client.get('/api/v1/transactions/', {'project': project1.id})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for transaction in data['results']:
            assert transaction['project'] == project1.id


@pytest.mark.django_db
class TestEquipmentViewSet:
    
    def test_list_equipment(self, api_client, equipment_data):
        Equipment.objects.create(**equipment_data)
        
        response = api_client.get('/api/v1/equipment/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_equipment(self, api_client, create_warehouse):
        warehouse = create_warehouse()
        equipment_data = {
            'name': 'Tower Crane TC-500',
            'status': 'operational',
            'location': 'Site B - Rosebank',
            'next_service': '2024-08-15',
            'serial_number': 'TC500-2024-001',
            'purchase_price': '5000000.00',
            'warehouse': warehouse.id,
        }
        response = api_client.post('/api/v1/equipment/', equipment_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'Tower Crane TC-500'
        assert data['id'].startswith('EQ-')
    
    def test_update_equipment_status(self, api_client, equipment_data):
        equipment = Equipment.objects.create(**equipment_data)
        
        response = api_client.patch(
            f'/api/v1/equipment/{equipment.id}/',
            {'status': 'maintenance'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'maintenance'
    
    def test_filter_equipment_by_status(self, api_client, equipment_data):
        equipment_data['status'] = 'operational'
        Equipment.objects.create(**equipment_data)
        equipment_data['id'] = str(uuid.uuid4())
        equipment_data['status'] = 'maintenance'
        Equipment.objects.create(**equipment_data)
        
        response = api_client.get('/api/v1/equipment/', {'status': 'operational'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for equip in data['results']:
            assert equip['status'] == 'operational'


@pytest.mark.django_db
class TestSafetyInspectionViewSet:
    
    def test_list_safety_inspections(self, api_client, safety_inspection_data, create_project):
        project = create_project()
        safety_inspection_data['project'] = project
        SafetyInspection.objects.create(**safety_inspection_data)
        
        response = api_client.get('/api/v1/safety-inspections/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_safety_inspection(self, api_client, create_project):
        project = create_project()
        inspection_data = {
            'site': 'Sandton Construction Site',
            'type': 'routine',
            'status': 'pending',
            'inspector': 'Safety Officer Nkosi',
            'project': project.id,
        }
        response = api_client.post('/api/v1/safety-inspections/', inspection_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['site'] == 'Sandton Construction Site'
    
    def test_update_inspection_status(self, api_client, safety_inspection_data, create_project):
        project = create_project()
        safety_inspection_data['project'] = project
        safety_inspection_data['status'] = 'pending'
        inspection = SafetyInspection.objects.create(**safety_inspection_data)
        
        response = api_client.patch(
            f'/api/v1/safety-inspections/{inspection.id}/',
            {'status': 'completed', 'findings': 'All safety measures in place'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'completed'
    
    def test_filter_inspections_by_type(self, api_client, create_project):
        project = create_project()
        SafetyInspection.objects.create(
            id=str(uuid.uuid4()),
            site='Site A',
            type='routine',
            status='completed',
            inspector='Inspector 1',
            project=project,
        )
        SafetyInspection.objects.create(
            id=str(uuid.uuid4()),
            site='Site B',
            type='emergency',
            status='pending',
            inspector='Inspector 2',
            project=project,
        )
        
        response = api_client.get('/api/v1/safety-inspections/', {'type': 'routine'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for inspection in data['results']:
            assert inspection['type'] == 'routine'


@pytest.mark.django_db
class TestDocumentViewSet:
    
    def test_list_documents(self, api_client, create_project):
        project = create_project()
        Document.objects.create(
            id=str(uuid.uuid4()),
            name='Blueprint.pdf',
            type='pdf',
            size='15 MB',
            author='Architect',
            project=project,
        )
        
        response = api_client.get('/api/v1/documents/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_document(self, api_client, create_project):
        project = create_project()
        document_data = {
            'name': 'Contract.pdf',
            'type': 'pdf',
            'size': '2.5 MB',
            'author': 'Legal Team',
            'project': project.id,
            'category': 'contracts',
        }
        response = api_client.post('/api/v1/documents/', document_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'Contract.pdf'
    
    def test_filter_documents_by_category(self, api_client, create_project):
        project = create_project()
        Document.objects.create(
            id=str(uuid.uuid4()),
            name='Blueprint.pdf',
            type='pdf',
            size='10 MB',
            author='Architect',
            project=project,
            category='blueprints',
        )
        Document.objects.create(
            id=str(uuid.uuid4()),
            name='Contract.pdf',
            type='pdf',
            size='2 MB',
            author='Legal',
            project=project,
            category='contracts',
        )
        
        response = api_client.get('/api/v1/documents/', {'category': 'blueprints'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for doc in data['results']:
            assert doc['category'] == 'blueprints'


@pytest.mark.django_db
class TestDashboardView:
    
    def test_get_dashboard_data(self, api_client, create_project):
        project = create_project(status='Active', budget=Decimal('5000000.00'))
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Expense',
            amount=Decimal('100000.00'),
            status='completed',
        )
        
        response = api_client.get('/api/v1/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'projects' in data
        assert 'financial' in data
        assert 'clients' in data
        assert 'employees' in data
        assert 'equipment' in data
        assert 'safety' in data
