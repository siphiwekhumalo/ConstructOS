import uuid
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, Transaction, Equipment, SafetyInspection, Document
from .serializers import (
    ProjectSerializer, TransactionSerializer, EquipmentSerializer,
    SafetyInspectionSerializer, DocumentSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'location']

    def perform_create(self, serializer):
        project_id = f"PRJ-{random.randint(100000, 999999)}"
        serializer.save(id=project_id)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer
    filterset_fields = ['status', 'type', 'category', 'project']
    search_fields = ['description']


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('-created_at')
    serializer_class = EquipmentSerializer
    filterset_fields = ['status', 'warehouse']
    search_fields = ['name', 'serial_number']

    def perform_create(self, serializer):
        equipment_id = f"EQ-{random.randint(100000, 999999)}"
        serializer.save(id=equipment_id)


class SafetyInspectionViewSet(viewsets.ModelViewSet):
    queryset = SafetyInspection.objects.all().order_by('-date')
    serializer_class = SafetyInspectionSerializer
    filterset_fields = ['status', 'type', 'project']
    search_fields = ['site', 'inspector']


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer
    filterset_fields = ['type', 'project', 'category']
    search_fields = ['name', 'author']


class DashboardView(APIView):
    def get(self, request):
        from backend.apps.crm.models import Client
        from backend.apps.erp.models import Employee

        projects = Project.objects.all()
        transactions = Transaction.objects.all()
        clients = Client.objects.all()
        employees = Employee.objects.all()
        equipment = Equipment.objects.all()
        inspections = SafetyInspection.objects.all()

        total_projects = projects.count()
        active_projects = projects.filter(status='Active').count()
        completed_projects = projects.filter(status='Completed').count()

        total_budget = sum(float(p.budget) for p in projects)
        total_expenses = sum(float(t.amount) for t in transactions)

        return Response({
            'projects': {
                'total': total_projects,
                'active': active_projects,
                'completed': completed_projects,
            },
            'financial': {
                'totalBudget': total_budget,
                'totalExpenses': total_expenses,
                'remaining': total_budget - total_expenses,
            },
            'clients': {
                'total': clients.count(),
            },
            'employees': {
                'total': employees.count(),
            },
            'equipment': {
                'total': equipment.count(),
                'active': equipment.filter(status='Active').count(),
            },
            'safety': {
                'totalInspections': inspections.count(),
                'passed': inspections.filter(status='Passed').count(),
            }
        })


class PowerBIConfigView(APIView):
    def get(self, request):
        import os
        workspace_id = os.environ.get('POWERBI_WORKSPACE_ID')
        report_id = os.environ.get('POWERBI_REPORT_ID')
        
        return Response({
            'configured': bool(workspace_id and report_id),
            'workspaceId': workspace_id,
            'reportId': report_id,
        })
