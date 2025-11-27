import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Account, Contact, Address, PipelineStage, Lead, Opportunity,
    Campaign, MailingList, Segment, Sla, Ticket, TicketComment, Client
)
from .serializers import (
    AccountSerializer, ContactSerializer, AddressSerializer, PipelineStageSerializer,
    LeadSerializer, OpportunitySerializer, CampaignSerializer, MailingListSerializer,
    SegmentSerializer, SlaSerializer, TicketSerializer, TicketCommentSerializer, ClientSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('-created_at')
    serializer_class = AccountSerializer
    filterset_fields = ['status', 'type', 'industry']
    search_fields = ['name', 'email']


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer
    filterset_fields = ['status', 'account']
    search_fields = ['first_name', 'last_name', 'email']


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by('-created_at')
    serializer_class = AddressSerializer
    filterset_fields = ['type', 'account', 'contact']


class PipelineStageViewSet(viewsets.ModelViewSet):
    queryset = PipelineStage.objects.all().order_by('order')
    serializer_class = PipelineStageSerializer


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-created_at')
    serializer_class = LeadSerializer
    filterset_fields = ['status', 'source', 'rating']
    search_fields = ['first_name', 'last_name', 'email', 'company']

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        lead = self.get_object()
        account = Account.objects.create(
            id=str(uuid.uuid4()),
            name=lead.company or f"{lead.first_name} {lead.last_name}",
            email=lead.email,
            phone=lead.phone,
            type='customer',
            status='active'
        )
        contact = Contact.objects.create(
            id=str(uuid.uuid4()),
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            title=lead.title,
            account=account,
            status='active',
            source=lead.source
        )
        from django.utils import timezone
        lead.converted_account = account
        lead.converted_contact = contact
        lead.converted_at = timezone.now()
        lead.status = 'converted'
        lead.save()
        return Response({
            'message': 'Lead converted successfully',
            'account_id': account.id,
            'contact_id': contact.id
        })


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all().order_by('-created_at')
    serializer_class = OpportunitySerializer
    filterset_fields = ['status', 'stage', 'account']
    search_fields = ['name']


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by('-created_at')
    serializer_class = CampaignSerializer
    filterset_fields = ['status', 'type']
    search_fields = ['name']


class MailingListViewSet(viewsets.ModelViewSet):
    queryset = MailingList.objects.all().order_by('-created_at')
    serializer_class = MailingListSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']


class SegmentViewSet(viewsets.ModelViewSet):
    queryset = Segment.objects.all().order_by('-created_at')
    serializer_class = SegmentSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']


class SlaViewSet(viewsets.ModelViewSet):
    queryset = Sla.objects.all().order_by('-created_at')
    serializer_class = SlaSerializer
    filterset_fields = ['is_active', 'priority']


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    filterset_fields = ['status', 'priority', 'type', 'assigned_to']
    search_fields = ['subject', 'ticket_number']

    def perform_create(self, serializer):
        import random
        ticket_number = f"TKT-{random.randint(100000, 999999)}"
        serializer.save(ticket_number=ticket_number)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == 'GET':
            comments = TicketComment.objects.filter(ticket=ticket).order_by('created_at')
            serializer = TicketCommentSerializer(comments, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = TicketCommentSerializer(data={**request.data, 'ticket': ticket.id})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketCommentViewSet(viewsets.ModelViewSet):
    queryset = TicketComment.objects.all().order_by('created_at')
    serializer_class = TicketCommentSerializer
    filterset_fields = ['ticket', 'is_internal']


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-created_at')
    serializer_class = ClientSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'company', 'email']
