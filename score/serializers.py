# api/serializers.py
from rest_framework import serializers
from .models import Offer, Lead, ScoreResult

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'name', 'value_props', 'ideal_use_cases']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'role', 'company', 'industry', 'location', 'linkedin_bio']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class ScoreResultSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='lead.name', read_only=True)
    role = serializers.CharField(source='lead.role', read_only=True)
    company = serializers.CharField(source='lead.company', read_only=True)

    class Meta:
        model = ScoreResult
        fields = ['id', 'name', 'role', 'company', 'intent', 'score', 'reasoning', 'offer', 'lead']
        read_only_fields = ['id', 'name', 'role', 'company', 'intent', 'score', 'reasoning', 'offer', 'lead']