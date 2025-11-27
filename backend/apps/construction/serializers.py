from rest_framework import serializers
from .models import Project, Transaction, Equipment, SafetyInspection, Document


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


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
