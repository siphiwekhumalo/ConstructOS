from rest_framework import serializers
from .models import (
    Account, Contact, Address, PipelineStage, Lead, Opportunity,
    Campaign, MailingList, Segment, Sla, Ticket, TicketComment, Client
)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'converted_at']


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MailingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailingList
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SlaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sla
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['id', 'ticket_number', 'created_at', 'updated_at', 'resolved_at', 'closed_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketComment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
