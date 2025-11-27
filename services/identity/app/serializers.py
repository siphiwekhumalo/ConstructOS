"""
Serializers for Identity/Contact Service.
"""
from rest_framework import serializers
from .models import User, Account, Contact, Address, AuditLog, Favorite, Event


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    roles = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'roles', 'department', 'phone', 'avatar_url',
            'azure_ad_object_id', 'azure_ad_roles', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'azure_ad_object_id', 'azure_ad_roles']
    
    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'account', 'contact', 'type', 'is_primary',
            'street', 'street2', 'city', 'state', 'postal_code', 'country',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id', 'account', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'mobile', 'title', 'department',
            'is_primary', 'is_active', 'do_not_call', 'do_not_email',
            'linkedin_url', 'notes', 'owner', 'addresses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccountSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'legal_name', 'account_number', 'type', 'tier',
            'industry', 'website', 'phone', 'email', 'status',
            'owner', 'owner_name', 'account_manager',
            'tax_id', 'vat_number', 'payment_terms', 'credit_limit', 'currency',
            'description', 'notes', 'last_synced_at', 'external_id',
            'contacts', 'addresses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'account_number', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        if obj.owner:
            return f"{obj.owner.first_name or ''} {obj.owner.last_name or ''}".strip()
        return None


class AccountLookupSerializer(serializers.ModelSerializer):
    """Lightweight serializer for autocomplete lookups."""
    billing_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_number', 'type',
            'payment_terms', 'credit_limit', 'billing_address'
        ]
    
    def get_billing_address(self, obj):
        address = obj.addresses.filter(type='billing', is_primary=True).first()
        if not address:
            address = obj.addresses.filter(is_primary=True).first()
        if address:
            return {
                'street': address.street,
                'city': address.city,
                'state': address.state,
                'postal_code': address.postal_code,
                'country': address.country,
            }
        return None


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'entity_type', 'entity_id',
            'changes', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.username
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'entity_type', 'entity_id',
            'entity_title', 'entity_subtitle', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'event_type', 'payload', 'status', 'retry_count',
            'source_service', 'correlation_id', 'error_message',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at']
