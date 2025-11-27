import uuid
import random
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, Transaction, Equipment, SafetyInspection, Document
from .serializers import (
    ProjectSerializer, TransactionSerializer, EquipmentSerializer,
    SafetyInspectionSerializer, DocumentSerializer
)
from backend.apps.core.storage_service import storage_service
from backend.apps.core.telemetry import traced, SpanContext


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
    parser_classes = [MultiPartParser, FormParser]
    
    @traced(name="document.upload", attributes={"component": "document_management"})
    @action(detail=False, methods=['post'], url_path='upload')
    def upload_file(self, request):
        """
        Upload a document to Azure Blob Storage.
        
        Expects multipart form data with:
        - file: The file to upload
        - project_id: Optional project ID
        - category: Optional category
        - author: Document author name
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided', 'code': 'NO_FILE'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        project_id = request.data.get('project_id')
        category = request.data.get('category')
        author = request.data.get('author', 'Unknown')
        
        if not storage_service.is_configured:
            document = Document.objects.create(
                id=str(uuid.uuid4()),
                name=uploaded_file.name,
                type=uploaded_file.content_type.split('/')[-1] if uploaded_file.content_type else 'unknown',
                size=self._format_file_size(uploaded_file.size),
                author=author,
                project_id=project_id,
                category=category,
                url=None,
            )
            serializer = self.get_serializer(document)
            return Response(
                {**serializer.data, 'warning': 'File storage not configured, metadata saved only'},
                status=status.HTTP_201_CREATED
            )
        
        with SpanContext("azure_blob_upload", {"filename": uploaded_file.name}) as span:
            result = storage_service.upload_document(
                file_data=uploaded_file,
                filename=uploaded_file.name,
                content_type=uploaded_file.content_type or 'application/octet-stream',
                project_id=project_id,
                category=category,
                metadata={'author': author}
            )
            
            if not result.get('success'):
                span.set_attribute("upload.success", False)
                error_code = result.get('error_code', 'UNKNOWN')
                
                if error_code == 'INVALID_CONTENT_TYPE':
                    return Response(
                        {'error': result.get('error'), 'code': error_code},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif error_code == 'FILE_TOO_LARGE':
                    return Response(
                        {'error': result.get('error'), 'code': error_code},
                        status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    )
                else:
                    return Response(
                        {'error': result.get('error', 'Upload failed'), 'code': error_code},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            span.set_attribute("upload.success", True)
            span.set_attribute("blob.name", result.get('blob_name'))
        
        blob_name = result.get('blob_name')
        try:
            document = Document.objects.create(
                id=str(uuid.uuid4()),
                name=result.get('sanitized_filename', uploaded_file.name),
                type=result.get('content_type', 'application/octet-stream').split('/')[-1],
                size=self._format_file_size(result.get('size', 0)),
                author=author,
                project_id=project_id,
                category=category,
                url=result.get('url'),
            )
        except Exception as e:
            if blob_name:
                storage_service.delete_document(blob_name)
            return Response(
                {'error': 'Failed to save document record', 'code': 'DB_ERROR'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @traced(name="document.download", attributes={"component": "document_management"})
    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        """
        Download a document from Azure Blob Storage.
        
        Returns a signed URL for secure access or the file content.
        """
        document = self.get_object()
        
        if not document.url:
            return Response(
                {'error': 'Document has no associated file', 'code': 'NO_FILE'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not storage_service.is_configured:
            return Response(
                {'download_url': document.url, 'warning': 'Direct URL returned - storage not configured'}
            )
        
        blob_name = self._extract_blob_name(document.url)
        
        if blob_name:
            result = storage_service.generate_sas_url(blob_name, expiry_minutes=15)
            if result.get('success'):
                return Response({
                    'download_url': result.get('url'),
                    'expires_in_minutes': result.get('expires_in_minutes')
                })
            else:
                return Response(
                    {'error': result.get('error'), 'code': result.get('error_code')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response({'download_url': document.url})
    
    @action(detail=True, methods=['delete'], url_path='remove-file')
    def remove_file(self, request, pk=None):
        """
        Remove the file from Azure Blob Storage and clear the document URL.
        """
        document = self.get_object()
        
        if document.url and storage_service.is_configured:
            blob_name = self._extract_blob_name(document.url)
            if blob_name:
                storage_service.delete_document(blob_name)
        
        document.url = None
        document.save()
        
        return Response({'message': 'File removed successfully'})
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _extract_blob_name(self, url: str) -> str:
        """Extract blob name from Azure Blob URL."""
        if not url:
            return None
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        parts = path.split('/', 1)
        if len(parts) > 1:
            return parts[1]
        return path


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
