import pytest
from decimal import Decimal
import uuid
from django.utils import timezone
from backend.apps.construction.models import (
    Project, Transaction, Equipment, SafetyInspection, Document
)


@pytest.mark.django_db
class TestProjectModel:
    
    def test_create_project(self, project_data, create_account, create_user):
        account = create_account()
        user = create_user()
        project_data['account'] = account
        project_data['manager'] = user
        project = Project.objects.create(**project_data)
        assert project.name == project_data['name']
        assert project.status == 'active'
        assert project.progress == 45
        assert project.budget == Decimal('15000000.00')
    
    def test_project_without_account(self, project_data):
        project = Project.objects.create(**project_data)
        assert project.account is None
        assert project.name == project_data['name']
    
    def test_project_progress_percentage(self, project_data):
        project_data['progress'] = 100
        project = Project.objects.create(**project_data)
        assert project.progress == 100
    
    def test_project_zero_progress(self, project_data):
        project_data['progress'] = 0
        project = Project.objects.create(**project_data)
        assert project.progress == 0
    
    def test_project_timestamps(self, project_data):
        project = Project.objects.create(**project_data)
        assert project.created_at is not None
        assert project.updated_at is not None
    
    def test_project_status_values(self):
        statuses = ['planning', 'active', 'on_hold', 'completed', 'cancelled']
        for status in statuses:
            project = Project.objects.create(
                id=str(uuid.uuid4()),
                name=f'Project {status}',
                location='Johannesburg',
                status=status,
                budget=Decimal('1000000.00'),
                due_date='2024-12-31',
            )
            assert project.status == status


@pytest.mark.django_db
class TestTransactionModel:
    
    def test_create_transaction(self, create_project):
        project = create_project()
        transaction = Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Construction materials purchase',
            amount=Decimal('250000.00'),
            status='completed',
            category='materials',
            type='expense',
        )
        assert transaction.description == 'Construction materials purchase'
        assert transaction.amount == Decimal('250000.00')
        assert transaction.type == 'expense'
    
    def test_transaction_without_project(self):
        transaction = Transaction.objects.create(
            id=str(uuid.uuid4()),
            description='General expense',
            amount=Decimal('5000.00'),
            status='pending',
            type='expense',
        )
        assert transaction.project is None
    
    def test_transaction_income_type(self, create_project):
        project = create_project()
        transaction = Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Client payment received',
            amount=Decimal('1000000.00'),
            status='completed',
            type='income',
        )
        assert transaction.type == 'income'
    
    def test_transaction_default_type(self, create_project):
        project = create_project()
        transaction = Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Test transaction',
            amount=Decimal('1000.00'),
            status='pending',
        )
        assert transaction.type == 'expense'
    
    def test_transaction_categories(self, create_project):
        project = create_project()
        categories = ['materials', 'labor', 'equipment', 'permits', 'subcontractors']
        for category in categories:
            transaction = Transaction.objects.create(
                id=str(uuid.uuid4()),
                project=project,
                description=f'{category} expense',
                amount=Decimal('10000.00'),
                status='completed',
                category=category,
            )
            assert transaction.category == category


@pytest.mark.django_db
class TestEquipmentModel:
    
    def test_create_equipment(self, equipment_data, create_warehouse, create_employee):
        warehouse = create_warehouse()
        employee = create_employee()
        equipment_data['warehouse'] = warehouse
        equipment_data['assigned_to'] = employee
        equipment = Equipment.objects.create(**equipment_data)
        assert equipment.name == equipment_data['name']
        assert equipment.status == 'operational'
        assert equipment.purchase_price == Decimal('2500000.00')
    
    def test_equipment_status_values(self):
        statuses = ['operational', 'maintenance', 'out_of_service', 'decommissioned']
        for status in statuses:
            equipment = Equipment.objects.create(
                id=str(uuid.uuid4()),
                name=f'Equipment {status}',
                status=status,
                location='Test Site',
                next_service='2024-06-15',
            )
            assert equipment.status == status
    
    def test_equipment_without_assignments(self, equipment_data):
        equipment = Equipment.objects.create(**equipment_data)
        assert equipment.warehouse is None
        assert equipment.assigned_to is None
    
    def test_equipment_timestamps(self, equipment_data):
        equipment = Equipment.objects.create(**equipment_data)
        assert equipment.created_at is not None
        assert equipment.updated_at is not None
    
    def test_equipment_serial_number(self, equipment_data):
        equipment = Equipment.objects.create(**equipment_data)
        assert equipment.serial_number == 'CAT320-2024-001'


@pytest.mark.django_db
class TestSafetyInspectionModel:
    
    def test_create_safety_inspection(self, safety_inspection_data, create_project):
        project = create_project()
        safety_inspection_data['project'] = project
        inspection = SafetyInspection.objects.create(**safety_inspection_data)
        assert inspection.site == safety_inspection_data['site']
        assert inspection.type == 'routine'
        assert inspection.status == 'completed'
    
    def test_inspection_without_project(self, safety_inspection_data):
        inspection = SafetyInspection.objects.create(**safety_inspection_data)
        assert inspection.project is None
    
    def test_inspection_types(self, create_project):
        project = create_project()
        inspection_types = ['routine', 'safety', 'compliance', 'emergency', 'audit']
        for insp_type in inspection_types:
            inspection = SafetyInspection.objects.create(
                id=str(uuid.uuid4()),
                site='Test Site',
                type=insp_type,
                status='pending',
                inspector='Test Inspector',
                project=project,
            )
            assert inspection.type == insp_type
    
    def test_inspection_findings_and_actions(self, safety_inspection_data, create_project):
        project = create_project()
        safety_inspection_data['project'] = project
        safety_inspection_data['findings'] = 'Missing safety signage on Level 3'
        safety_inspection_data['corrective_actions'] = 'Install required signage by end of week'
        inspection = SafetyInspection.objects.create(**safety_inspection_data)
        assert 'safety signage' in inspection.findings
        assert 'Install' in inspection.corrective_actions
    
    def test_inspection_status_values(self, create_project):
        project = create_project()
        statuses = ['pending', 'in_progress', 'completed', 'failed']
        for status in statuses:
            inspection = SafetyInspection.objects.create(
                id=str(uuid.uuid4()),
                site='Test Site',
                type='routine',
                status=status,
                inspector='Test Inspector',
                project=project,
            )
            assert inspection.status == status


@pytest.mark.django_db
class TestDocumentModel:
    
    def test_create_document(self, create_project):
        project = create_project()
        document = Document.objects.create(
            id=str(uuid.uuid4()),
            name='Project Blueprint v1.pdf',
            type='pdf',
            size='15.2 MB',
            author='John Architect',
            project=project,
            category='blueprints',
            url='https://storage.example.com/blueprints/v1.pdf',
            version=1,
        )
        assert document.name == 'Project Blueprint v1.pdf'
        assert document.type == 'pdf'
        assert document.version == 1
    
    def test_document_without_project(self):
        document = Document.objects.create(
            id=str(uuid.uuid4()),
            name='Company Policy.pdf',
            type='pdf',
            size='500 KB',
            author='HR Department',
            category='policies',
        )
        assert document.project is None
    
    def test_document_version_increment(self, create_project):
        project = create_project()
        doc_v1 = Document.objects.create(
            id=str(uuid.uuid4()),
            name='Specifications.pdf',
            type='pdf',
            size='2 MB',
            author='Engineer',
            project=project,
            version=1,
        )
        doc_v2 = Document.objects.create(
            id=str(uuid.uuid4()),
            name='Specifications.pdf',
            type='pdf',
            size='2.5 MB',
            author='Engineer',
            project=project,
            version=2,
        )
        assert doc_v2.version > doc_v1.version
    
    def test_document_categories(self, create_project):
        project = create_project()
        categories = ['blueprints', 'contracts', 'permits', 'reports', 'photos']
        for category in categories:
            document = Document.objects.create(
                id=str(uuid.uuid4()),
                name=f'{category}_doc.pdf',
                type='pdf',
                size='1 MB',
                author='Test Author',
                project=project,
                category=category,
            )
            assert document.category == category
    
    def test_document_default_version(self, create_project):
        project = create_project()
        document = Document.objects.create(
            id=str(uuid.uuid4()),
            name='New Document.pdf',
            type='pdf',
            size='100 KB',
            author='Test',
            project=project,
        )
        assert document.version == 1
