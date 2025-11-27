from rest_framework import serializers
from django.db.models import Sum
from datetime import date
from .models import Project, Transaction, Equipment, SafetyInspection, Document


class ProjectSerializer(serializers.ModelSerializer):
    progress_variance = serializers.SerializerMethodField()
    cost_variance = serializers.SerializerMethodField()
    health_status = serializers.SerializerMethodField()
    days_until_milestone = serializers.SerializerMethodField()
    open_issues_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_progress_variance(self, obj):
        """Return progress variance (actual - planned). Negative = behind schedule."""
        return obj.progress - obj.planned_progress
    
    def get_cost_variance(self, obj):
        """Return cost variance (budget - actual). Negative = over budget."""
        return float(obj.budget) - float(obj.actual_cost)
    
    def get_health_status(self, obj):
        """Determine project health based on progress and cost variance."""
        progress_var = obj.progress - obj.planned_progress
        budget = float(obj.budget) if obj.budget else 0
        cost_var_pct = ((float(obj.budget) - float(obj.actual_cost)) / budget * 100) if budget > 0 else 0
        
        if progress_var >= 0 and cost_var_pct >= -5:
            return 'on_track'
        elif progress_var >= -5 and cost_var_pct >= -10:
            return 'at_risk'
        else:
            return 'delayed'
    
    def get_days_until_milestone(self, obj):
        """Calculate days until next milestone."""
        if not obj.next_milestone_date:
            return None
        delta = obj.next_milestone_date - date.today()
        return max(0, delta.days)
    
    def get_open_issues_count(self, obj):
        """Count open safety inspections marked as 'Failed' or 'Needs Review'."""
        return SafetyInspection.objects.filter(
            project=obj,
            status__in=['Failed', 'Needs Review', 'In Progress']
        ).count()


class ProjectMetricsSerializer(serializers.Serializer):
    """Serializer for project portfolio metrics summary."""
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    on_track_count = serializers.IntegerField()
    at_risk_count = serializers.IntegerField()
    delayed_count = serializers.IntegerField()
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_actual_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    overall_cost_variance = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_progress = serializers.FloatField()


class ProjectCashflowSerializer(serializers.Serializer):
    """Serializer for project cashflow data points."""
    date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    cumulative = serializers.DecimalField(max_digits=15, decimal_places=2)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SafetyInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyInspection
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at']
