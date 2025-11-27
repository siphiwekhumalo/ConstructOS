"""
AI Module Models

Stores prediction results, model metadata, and training data references.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PredictionLog(models.Model):
    """Logs all AI predictions for auditing and model improvement."""
    
    PREDICTION_TYPES = [
        ('credit_risk', 'Credit Risk'),
        ('cashflow', 'Cash Flow Forecast'),
        ('lead_score', 'Lead Scoring'),
        ('project_delay', 'Project Delay'),
        ('maintenance', 'Predictive Maintenance'),
        ('demand', 'Demand Forecast'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    
    input_features = models.JSONField(default=dict)
    prediction_result = models.JSONField(default=dict)
    
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=20)
    confidence = models.FloatField(null=True, blank=True)
    
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_prediction_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prediction_type', 'entity_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.prediction_type} for {self.entity_type}:{self.entity_id}"


class ModelMetadata(models.Model):
    """Stores metadata about ML models."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    algorithm = models.CharField(max_length=100)
    features_used = models.JSONField(default=list)
    
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    training_data_size = models.IntegerField(null=True, blank=True)
    trained_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_model_metadata'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class FeatureStore(models.Model):
    """Stores computed features for ML models."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    feature_set = models.CharField(max_length=50)
    
    features = models.JSONField(default=dict)
    
    computed_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_feature_store'
        unique_together = ['entity_type', 'entity_id', 'feature_set']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.feature_set} for {self.entity_type}:{self.entity_id}"
