"""
Serializers for AI Module.
"""
from rest_framework import serializers
from .models import PredictionLog, ModelMetadata, FeatureStore


class PredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ModelMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelMetadata
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureStore
        fields = '__all__'
        read_only_fields = ['id', 'computed_at']


class CreditRiskRequestSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    include_history = serializers.BooleanField(default=True)


class CreditRiskResponseSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    customer_name = serializers.CharField(allow_null=True)
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()
    confidence = serializers.FloatField()
    factors = serializers.ListField(child=serializers.CharField())
    recommended_credit_limit = serializers.FloatField(allow_null=True)
    recommended_payment_terms = serializers.CharField(allow_null=True)
    model_info = serializers.DictField()
    predicted_at = serializers.DateTimeField()


class LeadScoreResponseSerializer(serializers.Serializer):
    lead_id = serializers.CharField()
    lead_name = serializers.CharField(allow_null=True)
    score = serializers.IntegerField()
    conversion_probability = serializers.FloatField()
    priority = serializers.CharField()
    factors = serializers.ListField()
    recommended_actions = serializers.ListField(child=serializers.CharField())
    model_info = serializers.DictField()
    predicted_at = serializers.DateTimeField()


class ProjectDelayResponseSerializer(serializers.Serializer):
    project_id = serializers.CharField()
    project_name = serializers.CharField(allow_null=True)
    delay_probability = serializers.FloatField()
    expected_delay_days = serializers.IntegerField()
    risk_level = serializers.CharField()
    risk_factors = serializers.ListField()
    mitigation_suggestions = serializers.ListField(child=serializers.CharField())
    model_info = serializers.DictField()
    predicted_at = serializers.DateTimeField()


class MaintenanceRiskResponseSerializer(serializers.Serializer):
    equipment_id = serializers.CharField()
    equipment_name = serializers.CharField(allow_null=True)
    failure_probability = serializers.FloatField()
    risk_level = serializers.CharField()
    estimated_remaining_life_days = serializers.IntegerField(allow_null=True)
    recommended_maintenance_date = serializers.DateField(allow_null=True)
    maintenance_type = serializers.CharField(allow_null=True)
    estimated_downtime_hours = serializers.FloatField(allow_null=True)
    parts_needed = serializers.ListField(child=serializers.CharField())
    model_info = serializers.DictField()
    predicted_at = serializers.DateTimeField()


class DemandForecastItemSerializer(serializers.Serializer):
    date = serializers.DateField()
    predicted_demand = serializers.FloatField()
    confidence_lower = serializers.FloatField()
    confidence_upper = serializers.FloatField()


class DemandForecastResponseSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    product_name = serializers.CharField(allow_null=True)
    warehouse_id = serializers.CharField(allow_null=True)
    forecast = DemandForecastItemSerializer(many=True)
    current_stock = serializers.FloatField(allow_null=True)
    reorder_point = serializers.FloatField(allow_null=True)
    suggested_order_quantity = serializers.FloatField(allow_null=True)
    stockout_risk_date = serializers.DateField(allow_null=True)
    model_info = serializers.DictField()
    predicted_at = serializers.DateTimeField()
