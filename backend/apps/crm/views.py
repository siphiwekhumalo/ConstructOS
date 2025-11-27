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

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """
        Get related data for an account - tickets and invoices.
        Used for the contextual side panel.
        """
        account = self.get_object()
        
        open_tickets = Ticket.objects.filter(
            account=account,
            status__in=['open', 'in_progress', 'pending']
        ).order_by('-created_at')[:5]
        
        tickets_data = [{
            'id': t.id,
            'ticket_number': t.ticket_number,
            'subject': t.subject,
            'status': t.status,
            'priority': t.priority,
            'created_at': t.created_at.isoformat(),
        } for t in open_tickets]
        
        from backend.apps.erp.models import Invoice
        recent_invoices = Invoice.objects.filter(
            account=account
        ).order_by('-created_at')[:5]
        
        invoices_data = [{
            'id': i.id,
            'invoice_number': i.invoice_number,
            'status': i.status,
            'total_amount': str(i.total_amount),
            'due_date': i.due_date.isoformat() if i.due_date else None,
            'created_at': i.created_at.isoformat(),
        } for i in recent_invoices]
        
        contacts = Contact.objects.filter(account=account).order_by('-is_primary', 'last_name')[:5]
        contacts_data = [{
            'id': c.id,
            'name': f"{c.first_name} {c.last_name}",
            'email': c.email,
            'title': c.title,
            'is_primary': c.is_primary,
        } for c in contacts]
        
        return Response({
            'open_tickets': tickets_data,
            'open_tickets_count': Ticket.objects.filter(
                account=account,
                status__in=['open', 'in_progress', 'pending']
            ).count(),
            'recent_invoices': invoices_data,
            'total_invoices': Invoice.objects.filter(account=account).count(),
            'contacts': contacts_data,
            'total_contacts': Contact.objects.filter(account=account).count(),
        })

    @action(detail=False, methods=['get'])
    def lookup(self, request):
        """
        Lookup accounts for autocomplete.
        Returns name, billing address, and payment terms.
        """
        term = request.query_params.get('term', '').strip()
        limit = int(request.query_params.get('limit', 10))
        
        if not term or len(term) < 2:
            return Response([])
        
        accounts = Account.objects.filter(
            name__icontains=term
        ).select_related('owner')[:limit]
        
        results = []
        for account in accounts:
            billing_address = account.get_primary_billing_address()
            results.append({
                'id': account.id,
                'name': account.name,
                'account_number': account.account_number,
                'type': account.type,
                'payment_terms': account.payment_terms,
                'credit_limit': str(account.credit_limit) if account.credit_limit else None,
                'billing_address': {
                    'street': billing_address.street if billing_address else None,
                    'city': billing_address.city if billing_address else None,
                    'state': billing_address.state if billing_address else None,
                    'postal_code': billing_address.postal_code if billing_address else None,
                    'country': billing_address.country if billing_address else None,
                } if billing_address else None,
            })
        
        return Response(results)


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
